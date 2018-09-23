from flask import (
        Blueprint, redirect, render_template,
        Response, request, url_for
)
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from project import db
from project.forms import RegisterForm, LoginForm, CodeForm, LobbyingTimeForm, ModeratedCaucusForm, AccountSettings
from project.models import User, Committee, Delegate, SpeakersList, Conference, Speech, GradingSystem, PointOfInformation, LobbyingTime, ModeratedCaucusing, mcSpeech
from project.flags_list import flags

import pycountry
import random
import time


users_bp = Blueprint('users', __name__)

def generate_code():
    code = ""
    for i in range(8):
        t = random.randint(0,2)
        if t == 0:
            code+=chr(random.randint(48,57))
        else:
            code+=chr(random.randint(97,122))
    return code

@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            confirm = form.confirm.data
            if password==confirm:
                user = User.query.filter_by(username=username).first()
                if user is None:
                    user = User(username, password)
                    user.user_type = "conference"
                    conf = Conference()
                    conf.username = username
                    conf.committees_number = 0
                    conf.delegates_number = 0
                    db.session.add(conf)
                    db.session.add(user)
                    db.session.commit()
                    gs = GradingSystem()
                    conf = Conference.query.filter_by(username=username).first()
                    gs.conference = conf.id
                    gs.poi_bad = 0
                    gs.poi_good = 2
                    gs.mc_bad = 0
                    gs.mc_good = 2
                    gs.speech_bad = 1
                    gs.speech_good = 3
                    db.session.add(gs)
                    db.session.commit()
                    login_user(user, remember=True)
                    return redirect(url_for('private_route'))
    else:
        return render_template('register.html', form=form)

@users_bp.route('/edit',methods=['GET','POST'])
@login_required
def edit():
    form = AccountSettings(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = current_user
            conf = Conference.query.filter_by(username=current_user.username).first()
            new_username = form.username.data
            old_password = form.old_password.data
            new_password = form.new_password.data
            confirm = form.confirm.data
            if user.check_password(old_password) and new_password==confirm:
                if new_username!="":
                    user.username = new_username
                    conf.username = new_username
                if new_password!="":
                    user.set_password(new_password)
                db.session.commit()
                if current_user.username == new_username:
                    return redirect(url_for('private_route'))
                else:
                    return('fuck')
            else:
                return Response('<p>Failure due to either:</p><ul><li>The password you entered is incorrect.</li>or<li>The new password does not match the password you entered in the confirmation field.</li></ul>')
        else:
            return Response('<p>Invalid form</p>')

@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if user is None or not user.check_password(password):
                return Response("<p>Incorrect username or password</p>")
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('private_route')
            return redirect(next_page)
        else:
            return Response('<p>Invalid form</p>')
    return render_template('login.html', form=form)

@users_bp.route('/add_committee', methods=['GET','POST'])
@login_required
def add_committee():
    conference = Conference.query.filter_by(username=current_user.username).first()
    all_countries = list(pycountry.countries)
    countries = []
    for c in all_countries:
        countries.append((c,flags[c.name]))
    if request.method == 'POST':
        committee = Committee()
        committee.committee = request.form.get('committee')
        committee.conference = conference.id
        committee.topic = request.form.get('topic')
        committee.code = generate_code()
        com = Committee.query.filter_by(code=committee.code).first()
        while(not(com is None)):
            committee.code = generate_code()
            com = Committee.query.filter_by(code=committee.code).first()
        committee.countries = ""
        user = User(committee.code, committee.code)
        user.user_type = "committee"
        db.session.add(user)
        db.session.add(committee)
        db.session.commit()
        for c in all_countries:
            if request.form.get(c.name) is not None:
                delegate = Delegate()
                delegate.country = c.alpha_2
                delegate.committee = committee.id
                delegate.points = 0
                delegate.participations = 0
                db.session.add(delegate)
                db.session.commit()
                if committee.countries == "":
                    committee.countries = c.alpha_2
                else:
                    committee.countries += " "+c.alpha_2
        db.session.commit()
        return redirect(url_for('private_route'))
    else:
        return render_template('add_committee.html', countries=countries)

@users_bp.route('/enter_committee', methods=['GET','POST'])
def enter_committee():
    form = CodeForm(request.form)
    if request.method == 'POST':
        code = form.code.data
        committee = Committee.query.filter_by(code=code).first()
        user = User.query.filter_by(username=code).first()
        if not(committee is None):
            login_user(user, remember=True)
            return redirect(url_for('committee'))
        else:
            return("No committee")

@users_bp.route('/delete_committee/<int:committee>')
@login_required
def delete_committee(committee):
    committee = Committee.query.filter_by(id=committee).first()
    confuser = Conference.query.filter_by(username=current_user.username).first()
    if confuser.id == committee.conference:
        delegates = Delegate.query.filter_by(committee=committee.id).all()
        lists = SpeakersList.query.filter_by(committee=committee.id).all()
        for d in delegates:
            db.session.delete(d)
        for s in lists:
            s.delete()
        comuser = User.query.filter_by(username=committee.code).first()
        db.session.delete(comuser)
        db.session.delete(committee)
        db.session.commit()
        return redirect(url_for('private_route'))
    else:
        logout_user()
        return("Not allowed")

@users_bp.route('/create_list')
@login_required
def speakers():
    com = Committee.query.filter_by(code=current_user.username).first()
    current = SpeakersList.query.filter_by(committee=com.id, finish_time=-1).first()
    if current is None:
        sp_list = SpeakersList()
        sp_list.committee = com.id
        sp_list.countries = ""
        sp_list.start_time = (time.localtime(time.time())[3]*100)+time.localtime(time.time())[4]
        sp_list.finish_time = -1
        sp_list.speaker_time = 60
        db.session.add(sp_list)
        db.session.commit()
    else:
        sp_list = current
    if sp_list.countries == "":
        return redirect(url_for('speakers', sp_id=sp_list.id))
    else:
        return redirect(url_for('users.start_speakers_list',sp_id=sp_list.id))

@users_bp.route('/addtolist/<int:sp_id>/<del_con>')
@login_required
def add_speaker(sp_id,del_con):
    sp_list = SpeakersList.query.filter_by(id=sp_id).first()
    speech = Speech()
    speech.speakers_list = sp_id
    speech.delegate = Delegate.query.filter_by(country=del_con, committee=sp_list.committee).first().id
    speech.pois = ""
    db.session.add(speech)
    if sp_list.countries == "":
        sp_list.countries = del_con
    else:
        sp_list.countries += " "+del_con
    db.session.commit()
    return redirect(url_for('speakers', sp_id=sp_list.id))

@users_bp.route('/removefromlist/<int:sp_id>/<del_con>')
@login_required
def remove_speaker(sp_id,del_con):
    sp_list = SpeakersList.query.filter_by(id=sp_id).first()
    delegate = Delegate.query.filter_by(country=del_con, committee=sp_list.committee).first()
    speech = Speech.query.filter_by(speakers_list=sp_list.id, delegate=delegate.id).first()
    db.session.delete(speech)
    sp_list.countries.lstrip()
    countries = sp_list.countries.split(" ")
    if len(countries) == 1:
        sp_list.countries = ""
    elif countries.index(del_con) == 0:
        countries = sp_list.countries.split(del_con+" ")
        sp_list.countries = countries[1]
    elif countries.index(del_con) == len(countries)-1:
        countries = sp_list.countries.split(" "+del_con)
        sp_list.countries = countries[0]
    else:
        countries = sp_list.countries.split(" "+del_con)
        sp_list.countries = countries[0]+countries[1]
    db.session.commit()
    return redirect(url_for('speakers', sp_id=sp_list.id))

@users_bp.route('/gradespeech/<int:speech>/<int:grading>')
@login_required
def grade_speech(speech, grading):
    speech = Speech.query.filter_by(id=speech).first()
    sp_list = SpeakersList.query.filter_by(id=speech.speakers_list).first()
    delegate = Delegate.query.filter_by(id=speech.delegate).first()
    com = Committee.query.filter_by(id=delegate.committee).first()
    gs = GradingSystem.query.filter_by(conference=com.conference).first()
    sp_delegates_str = sp_list.countries.lstrip().split(" ")
    index = sp_delegates_str.index(delegate.country)
    if index != len(sp_delegates_str)-1:
        next_speaker = sp_delegates_str[index+1]
    else:
        next_speaker = "done"
    if grading == 0:
        delegate.points += gs.speech_bad
    elif grading == 1:
        delegate.points += gs.speech_good
    delegate.participations += 1
    db.session.commit()
    return redirect(url_for('speaker', sp_id=sp_list.id, del_con=next_speaker))

@users_bp.route('/startspeakerslist/<int:sp_id>')
@login_required
def start_speakers_list(sp_id):
    sp_list = SpeakersList.query.filter_by(id=sp_id).first()
    sp_list.countries.lstrip()
    del_con = sp_list.countries.split(" ")[0]
    return redirect(url_for('speaker', sp_id=sp_id, del_con=del_con))

@users_bp.route('/addPoI/<int:speech>/<del_con>')
@login_required
def add_POI(speech, del_con):
    speech = Speech.query.filter_by(id=speech).first()
    sp_list = SpeakersList.query.filter_by(id=speech.speakers_list).first()
    poi_delegate = Delegate.query.filter_by(committee=sp_list.committee, country=del_con).first()
    if speech.pois == "":
        speech.pois = del_con
    else:
        speech.pois += " "+del_con
    poi = PointOfInformation()
    poi.speech = speech.id
    poi.delegate = poi_delegate.id
    poi.grading = 0
    db.session.add(poi)
    db.session.commit()
    delegate = Delegate.query.filter_by(id=speech.delegate).first()
    return redirect(url_for('speaker', sp_id=speech.speakers_list, del_con=delegate.country))

@users_bp.route('/removePOI/<int:speech>/<del_con>')
@login_required
def remove_POI(speech, del_con):
    speech = Speech.query.filter_by(id=speech).first()
    sp_list = SpeakersList.query.filter_by(id=speech.speakers_list).first()
    delegate = Delegate.query.filter_by(committee=sp_list.committee, country=del_con).first()
    poi = PointOfInformation.query.filter_by(speech=speech.id, delegate=delegate.id).first()
    db.session.delete(poi)
    countries = speech.pois.lstrip().split(" ")
    if len(countries) == 1:
        speech.pois = ""
    elif countries.index(del_con) == 0:
        countries = speech.pois.lstrip().split(del_con+" ")
        speech.pois = countries[1]
    elif countries.index(del_con) == len(countries)-1:
        countries = speech.pois.lstrip().split(" "+del_con)
        speech.pois = countries[0]
    else:
        countries = speech.pois.lstrip().split(" "+del_con)
        speech.pois = countries[0]+countries[1]
    db.session.commit()
    delegate = Delegate.query.filter_by(id=speech.delegate).first()
    return redirect(url_for('speaker', sp_id=speech.speakers_list, del_con=delegate.country))

@users_bp.route('/gradePOI/<int:poi>/<int:grading>')
@login_required
def grade_POI(poi, grading):
    POI = PointOfInformation.query.filter_by(id=poi).first()
    speech = Speech.query.filter_by(id=POI.speech).first()
    sp_list = SpeakersList.query.filter_by(id=speech.speakers_list).first()
    com = Committee.query.filter_by(id=sp_list.committee).first()
    gs = GradingSystem.query.filter_by(conference=com.conference).first()
    delegate = Delegate.query.filter_by(id=POI.delegate).first()
    if grading == 0:
        POI.grading = -1
        delegate.points = delegate.points+gs.poi_bad
    elif grading == 1:
        POI.grading = 1
        delegate.points = delegate.points+gs.poi_good
    delegate.participations = delegate.participations+1
    db.session.commit()
    return redirect(url_for('speaker', sp_id=sp_list.id, del_con=Delegate.query.filter_by(id=speech.delegate).first().country))

@users_bp.route('/gradeMC/<int:mc_sp>/<int:grading>')
@login_required
def grade_MC(mc_sp, grading):
    speech = mcSpeech.query.filter_by(id=mc_sp).first()
    mc = ModeratedCaucusing.query.filter_by(id=speech.caucusing).first()
    com = Committee.query.filter_by(id=mc.committee).first()
    gs = GradingSystem.query.filter_by(conference=com.conference).first()
    delegate = Delegate.query.filter_by(id=speech.delegate).first()
    if grading == 0:
        #POI.grading = -1
        delegate.points = delegate.points+gs.mc_bad
    elif grading == 1:
        #POI.grading = 1
        delegate.points = delegate.points+gs.mc_good
    delegate.participations = delegate.participations+1
    db.session.commit()
    return redirect(url_for('mc_speaker', mc_sp_id=speech.id))

@users_bp.route('/lobbyingTime', methods=['GET','POST'])
@login_required
def lobbyingTime():
    form = LobbyingTimeForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            com = Committee.query.filter_by(code=current_user.username).first()
            current = LobbyingTime.query.filter_by(committee=com.id, finish_time=-1).first()
            if (current is None):
                lt = False
            elif (time.time()-current.start_time>current.duration):
                current.finish_time = time.time()
                lt = False
            else:
                lt = True
            if not lt:
                lt = LobbyingTime()
                lt.committee = com.id
                lt.start_time = time.time()
                lt.finish_time = -1
                mins = form.minutes.data
                if mins is None:
                    mins = 0
                secs = form.seconds.data
                if secs is None:
                    secs = 0
                lt.duration = mins*60+secs
                db.session.add(lt)
                db.session.commit()
            else:
                lt = current
            return redirect(url_for('lobbyingTime',lt_id=lt.id))
        else:
            return('invalid form')

@users_bp.route('/moderatedCaucusing', methods=['GET','POST'])
@login_required
def moderatedCaucusing():
    form = ModeratedCaucusForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            com = Committee.query.filter_by(code=current_user.username).first()
            mc = ModeratedCaucusing()
            mc.committee = com.id
            mc.topic = form.topic.data
            mc.start_time = (time.localtime(time.time())[3]*100)+time.localtime(time.time())[4]
            mc.finish_time = -1
            mc.countries = ""
            mins = form.minutes.data
            if mins is None:
                mins = 0
            secs = form.seconds.data
            if secs is None:
                secs = 0
            mc.speaker_time = mins*60+secs
            db.session.add(mc)
            db.session.commit()
            mc = ModeratedCaucusing.query.filter_by(committee=com.id, start_time=mc.start_time).first()
            return redirect(url_for('mcChooseCountry', mc_id=mc.id))
        else:
            return('invalid form')

@users_bp.route('/createMCspeaker/<mc_id>/<del_con>')
@login_required
def createMCspeaker(mc_id, del_con):
    mc = ModeratedCaucusing.query.filter_by(id=mc_id).first()
    speech = mcSpeech()
    speech.caucusing = mc_id
    speech.delegate = Delegate.query.filter_by(country=del_con, committee=mc.committee).first().id
    db.session.add(speech)
    if mc.countries == "":
        mc.countries = del_con
    else:
        mc.countries += " "+del_con
    db.session.commit()
    return redirect(url_for('mc_speaker', mc_sp_id=speech.id))


@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))