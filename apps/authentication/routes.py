"""authentication routes file"""

from flask import render_template, request, flash
from flask_login import logout_user, login_required, current_user

from apps.authentication import blueprint
from apps.authentication.functions import sign_in, redirect_url, sign_up
from apps.authentication.forms import LoginForm, SignupForm


@blueprint.route('/signin', methods=['POST', 'GET'])
def signin_page():
    """Signing page"""
    login_form = LoginForm()

    if request.method == 'POST':
        sign_in(form=login_form)
        return redirect_url('dashboard_blueprint.dashboard_page')

    return render_template('./sign-in.html',
        login_form=login_form)


@blueprint.route('/signup', methods=['POST', 'GET'])
def signup_page():
    """sign up page"""
    signup_form = SignupForm()
    if request.method == 'POST':
        if signup_form.password1.data == signup_form.password2.data:
            sign_up(signup_form)
            return redirect_url('authentication_blueprint.signin_page')
        else:
            flash('Password does not match!', category='danger')
            return redirect_url('authentication_blueprint.signup_page')


    return render_template('./sign-up.html', signup_form=signup_form)


@blueprint.route('/signout')
@login_required
def signout_page():
    """sig out route app"""  
    logout_user()

    return redirect_url('authentication_blueprint.signin_page')