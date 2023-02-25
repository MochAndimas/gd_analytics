"""From file"""

from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, IntegerField, TextAreaField, BooleanField
from wtforms.validators import Email, DataRequired, Regexp, Length, ValidationError, EqualTo
from apps.authentication.models import Account


class LoginForm(FlaskForm):
    """login form"""
    email_address = EmailField(
        id='login-email',
        label='Email Address :',
        validators=[
            Email(),
            DataRequired()
        ]
    )
    password = PasswordField(
        id='login-password',
        label='Password :',
        validators=[
            DataRequired()
        ]
    )
    check = BooleanField(
        id='rememberMe',
        label='Remember Me')
    submit = SubmitField(id='sign-in', label='Sign In')


class SignupForm(FlaskForm):
    """sign up form"""
    email_address = EmailField(
        id='signup-email',
        label='Email Address :',
        validators=[
            Email(),
            DataRequired()
        ]
    )
    role = StringField(
        id='id-role',
        label='Role :',
        validators=[DataRequired()]
        )
    password1 = PasswordField(
        id='password1',
        label='Password :',
        validators=[
            DataRequired()
        ]
    )
    password2 = PasswordField(
        id='password2',
        label='Re-type password :',
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField(id='sign-up', label='Sign Up')