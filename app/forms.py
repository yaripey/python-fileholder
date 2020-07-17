from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo

from flask_wtf.file import FileField, FileRequired, FileAllowed

from app.models import User
from app.models import File

from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class FileForm(FlaskForm):
    file = FileField("Choose a file", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'txt'], 'Unaccaptable file format.')
        ])
    expiration = SelectField(
        "Choose your file expiration time.",
        choices=[
            (1, '1 minute'),
            (10, '10 minutes'),
            (30, '30 minutes'),
            (60, '1 hours'),
            (300, '5 hours'),
            (1440, '1 day'),
            (4320, '3 days'),
            (10080, '7 days')
        ],
        validate_choice = False
    )
    submit = SubmitField('Upload')


