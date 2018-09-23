from flask_wtf import Form
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange


class RegisterForm(Form):
    username = StringField('Username', validators=[DataRequired(), Length(max=40)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=40)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired(), Length(max=40)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=40)])

class CodeForm(Form):
	code = StringField('Code', validators=[DataRequired(),Length(min=8,max=8)])

class LobbyingTimeForm(Form):
	minutes = IntegerField('minutes', validators=[NumberRange(min=0,max=59)])
	seconds = IntegerField('seconds', validators=[NumberRange(min=0,max=59)])

class ModeratedCaucusForm(Form):
	topic = StringField('topic', validators=[DataRequired()])
	minutes = IntegerField('minutes', validators=[NumberRange(min=0,max=59)])
	seconds = IntegerField('seconds', validators=[NumberRange(min=0,max=59)])

class AccountSettings(Form):
    username = StringField('Username', validators=[Length(max=40)])
    old_password = PasswordField('Old Password', validators=[DataRequired(), Length(max=40)])
    new_password = PasswordField('New Password', validators=[Length(max=40)])
    confirm = PasswordField('Confirm Password', validators=[EqualTo('new_password')])