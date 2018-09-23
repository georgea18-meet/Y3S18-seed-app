from project import db

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    user_type = db.Column(db.String)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def return_type(self):
        return "user"

    def __repr__(self):
        return 'User %d %s' % (self.id, self.username)

class Conference(db.Model):

    __tablename__ = "conferences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    committees_number = db.Column(db.Integer)
    delegates_number = db.Column(db.Integer)


class Committee(db.Model):

    __tablename__ = "committees"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    committee = db.Column(db.String, nullable=False)
    conference = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String)
    code = db.Column(db.String, unique=True, nullable=False)
    countries = db.Column(db.String)

class Delegate(db.Model):

    __tablename__ = "delegates"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String, nullable=False)
    committee = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer)
    participations = db.Column(db.Integer)

class SpeakersList(db.Model):

    __tablename__ = "speakerslists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    committee = db.Column(db.Integer, nullable=False)
    countries = db.Column(db.String)
    start_time = db.Column(db.Integer)
    finish_time = db.Column(db.Integer)
    speaker_time = db.Column(db.Integer)

    def delete(self):
        speeches = Speech.query.filter_by(speakers_list=self.id).all()
        for s in speeches:
            db.session.delete(s)
        db.session.delete(self)
        db.session.commit()

class ModeratedCaucusing(db.Model):

    __tablename__ = "moderatedcaucusings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    committee = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String)
    countries = db.Column(db.String)
    start_time = db.Column(db.Integer)
    finish_time = db.Column(db.Integer)
    speaker_time = db.Column(db.Integer)

class Speech(db.Model):

    __tablename__ = "speeches"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    speakers_list = db.Column(db.Integer, nullable=False)
    delegate = db.Column(db.Integer, nullable=False)
    pois = db.Column(db.String)

class mcSpeech(db.Model):

    __tablename__ = "mcspeeches"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    caucusing = db.Column(db.Integer, nullable=False)
    delegate = db.Column(db.Integer, nullable=False)

class GradingSystem(db.Model):

    __tablename__ = "gradingsystems"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conference = db.Column(db.Integer, unique=True, nullable=False)
    poi_bad = db.Column(db.Integer)
    poi_good = db.Column(db.Integer)
    mc_bad = db.Column(db.Integer)
    mc_good = db.Column(db.Integer)
    speech_bad = db.Column(db.Integer)
    speech_good = db.Column(db.Integer)

class PointOfInformation(db.Model):

    __tablename__ = "pointsofinformation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    speech = db.Column(db.Integer, nullable=False)
    delegate = db.Column(db.Integer, nullable=False)
    grading = db.Column(db.Integer)

class LobbyingTime(db.Model):

    __tablename__ = "lobbyingtimes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    committee = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Integer)
    finish_time = db.Column(db.Integer)
    duration = db.Column(db.Integer)

# TODO: Create your other models here
class YourModel(db.Model):
    
    __tablename__ = "yourmodel"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # fill in the rest of your fields and methods!
