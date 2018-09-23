from flask import (
        Blueprint, redirect, render_template,
        Response, request, url_for
)
from flask import render_template
from flask_login import login_required, current_user
from project import db
from project.forms import RegisterForm, LoginForm, CodeForm, LobbyingTimeForm, ModeratedCaucusForm, AccountSettings
from project.models import User, Committee, Delegate, SpeakersList, Speech, PointOfInformation, LobbyingTime, ModeratedCaucusing, mcSpeech
from project.flags_list import flags

import pycountry, time, math

from . import app


@app.route('/')
def index():
	if not current_user.is_authenticated:
		loginform = LoginForm(request.form)
		signupform = RegisterForm(request.form)
		codeform = CodeForm(request.form)
		return render_template('index.html', loginform = loginform, signupform=signupform, codeform=codeform)
	elif current_user.user_type == "conference":
		return redirect(url_for('private_route'))
	else:
		return redirect(url_for('committee'))

@app.route('/private')
@login_required
def private_route():
	accountsettingsform = AccountSettings(request.form)
	committiees = Committee.query.filter_by(conference=current_user.id).all()
	return render_template('private.html', committiees=committiees, accountsettingsform = AccountSettings(request.form))

@app.route('/committee')
@login_required
def committee():
	lobbyingtimeform = LobbyingTimeForm(request.form)
	moderatedcaucusform = ModeratedCaucusForm(request.form)
	committee = Committee.query.filter_by(code=current_user.username).first()
	current = LobbyingTime.query.filter_by(committee=committee.id, finish_time=-1).first()
	if (current is None):
		lt = False
	elif (time.time()-current.start_time>current.duration):
		current.finish_time = time.time()
		lt = False
	else:
		lt = True
	countries = committee.countries.lstrip().split(" ")
	delegates = []
	for c in countries:
		if c != "":
			delegates.append((pycountry.countries.get(alpha_2=c),flags[pycountry.countries.get(alpha_2=c).name]))
	return render_template('committee.html', committee=committee, delegates=delegates, lobbyingtimeform=lobbyingtimeform, lt=lt, lt_ob=current, moderatedcaucusform=moderatedcaucusform)

@app.route('/speakerslist/<int:sp_id>')
@login_required
def speakers(sp_id):
	com = Committee.query.filter_by(code=current_user.username).first()
	no_flags = db.session.query(Delegate).filter_by(committee=com.id).all()
	delegates = []
	sp_delegates = []
	sp_list = SpeakersList.query.filter_by(id=sp_id).first()
	sp_list.countries.lstrip()
	sp_delegates_str = sp_list.countries.split(" ")
	for n in no_flags:
		if not(n.country in sp_delegates_str):
			delegates.append((n,flags[pycountry.countries.get(alpha_2=n.country).name],pycountry.countries.get(alpha_2=n.country).name))
	for c in sp_delegates_str:
		if c != "":
			sp_delegates.append((pycountry.countries.get(alpha_2=c),flags[pycountry.countries.get(alpha_2=c).name]))
	return render_template('speakers_list.html', delegates=delegates, sp_list=sp_list, sp_delegates=sp_delegates)

@app.route('/speaker/<int:sp_id>/<del_con>')
@login_required
def speaker(sp_id,del_con):
	sp_list = SpeakersList.query.filter_by(id=sp_id).first()
	if del_con == "done":
		sp_list.finish_time = (time.localtime(time.time())[3]*100)+time.localtime(time.time())[4]
		db.session.commit()
		return redirect(url_for('committee'))
	else:
		com = Committee.query.filter_by(code=current_user.username).first()
		delegate = Delegate.query.filter_by(country=del_con, committee=com.id).first()
		current_speaker = (delegate,flags[pycountry.countries.get(alpha_2=delegate.country).name],pycountry.countries.get(alpha_2=delegate.country).name)
		no_flags = db.session.query(Delegate).filter_by(committee=com.id).all()
		delegates = []
		sp_delegates = []
		all_delegates = []
		speech = Speech.query.filter_by(delegate=delegate.id, speakers_list=sp_list.id).first()
		points = speech.pois.lstrip().split(" ")
		POIs = []
		speaker_time = sp_list.speaker_time
		sp_list.countries.lstrip()
		sp_delegates_str = sp_list.countries.split(" ")
		index = sp_delegates_str.index(current_speaker[0].country)
		if index != len(sp_delegates_str)-1:
			next_speaker = sp_delegates_str[index+1]
		else:
			next_speaker = sp_delegates_str[0]
		for n in no_flags:
			if n.country in points:
				all_delegates.append((n,flags[pycountry.countries.get(alpha_2=n.country).name],pycountry.countries.get(alpha_2=n.country).name,True))
			elif not(n.country in points):
				all_delegates.append((n,flags[pycountry.countries.get(alpha_2=n.country).name],pycountry.countries.get(alpha_2=n.country).name,False))
			if not(n.country in sp_delegates_str):
				delegates.append((n,flags[pycountry.countries.get(alpha_2=n.country).name],pycountry.countries.get(alpha_2=n.country).name))
		for c in sp_delegates_str:
			if c != "":
				sp_delegates.append((pycountry.countries.get(alpha_2=c),flags[pycountry.countries.get(alpha_2=c).name]))
		for p in points:
			if p != "":
				poi_delegate = Delegate.query.filter_by(committee=sp_list.committee, country=p).first()
				poi = PointOfInformation.query.filter_by(speech=speech.id, delegate=poi_delegate.id).first()
				POIs.append((pycountry.countries.get(alpha_2=p),flags[pycountry.countries.get(alpha_2=p).name],p,poi))
		return render_template('speaker.html', POIs=POIs ,speaker_time=speaker_time, delegates=delegates, sp_list=sp_list, sp_delegates=sp_delegates, current_speaker=current_speaker, next_speaker=next_speaker, all_delegates=all_delegates, speech=speech)

@app.route('/results')
@login_required
def results():
	com = Committee.query.filter_by(code=current_user.username).first()
	dels = Delegate.query.filter_by(committee=com.id).order_by(Delegate.points).all()
	dels.reverse()
	delegates_sorted = []
	highest = dels[0].points
	for i in range(highest+1):
		delegates_participations = []
		delegates_same = Delegate.query.filter_by(points=i,committee=com.id).all()
		for d in delegates_same:
			delegates_participations.append((d.participations,d.id))
		delegates_participations.sort()
		delegates_participations.reverse()
		for v in delegates_participations:
			delegates_sorted.append(Delegate.query.filter_by(id=v[1]).first())
	delegates_sorted.reverse()
	delegates = []
	for n in delegates_sorted:
		if n.participations == 0:
			quality = '-'
		else:
			quality = str(n.points/n.participations)
		delegates.append((n,flags[pycountry.countries.get(alpha_2=n.country).name],pycountry.countries.get(alpha_2=n.country).name,quality))
	return render_template('results.html', delegates=delegates)

@app.route('/lobbyingTime/<int:lt_id>')
@login_required
def lobbyingTime(lt_id):
	lt = LobbyingTime.query.filter_by(id=lt_id).first()
	timer_time = math.ceil(lt.duration-(time.time()-lt.start_time))
	if timer_time>0:
		secs = timer_time%60
		mins = int((timer_time-secs)/60)
		if secs<10:
			secs='0'+str(secs)
		if mins<10:
			mins='0'+str(mins)
	else:
		secs = '00'
		mins = '00'
	return render_template('lobbying.html',timer_time=timer_time,mins=mins,secs=secs)

@app.route('/moderatedcaucusing/pick/<int:mc_id>')
@login_required
def mcChooseCountry(mc_id):
	com = Committee.query.filter_by(code=current_user.username).first()
	all_countries = db.session.query(Delegate).filter_by(committee=com.id).all()
	delegates = []
	mc = ModeratedCaucusing.query.filter_by(id=mc_id).first()
	for n in all_countries:
		delegates.append((n,flags[pycountry.countries.get(alpha_2=n.country).name],pycountry.countries.get(alpha_2=n.country).name))
	return render_template('mc_countries.html', delegates=delegates, topic=mc.topic, mc_id=mc.id)

@app.route('/moderatedcaucusing/speech/<int:mc_sp_id>')
@login_required
def mc_speaker(mc_sp_id):
	com = Committee.query.filter_by(code=current_user.username).first()
	speech = mcSpeech.query.filter_by(id=mc_sp_id).first()
	mc = ModeratedCaucusing.query.filter_by(id=speech.caucusing).first()
	delegate = Delegate.query.filter_by(id=speech.delegate).first()
	current_speaker = (delegate,flags[pycountry.countries.get(alpha_2=delegate.country).name],pycountry.countries.get(alpha_2=delegate.country).name)
	speaker_time = mc.speaker_time
	all_countries = db.session.query(Delegate).filter_by(committee=com.id).all()
	delegates = []
	for n in all_countries:
		delegates.append((n,flags[pycountry.countries.get(alpha_2=n.country).name],pycountry.countries.get(alpha_2=n.country).name))
	return render_template('mc.html', current_speaker=current_speaker, speaker_time=speaker_time, delegates=delegates, mc_id=mc.id, mc_sp=mc_sp_id)

@app.route('/invalid/<int:msg>')
def error(msg):
	titles = ["Invalid input!"]
	return render_template('error.html',title=titles[msg])