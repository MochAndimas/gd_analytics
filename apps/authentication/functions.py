from datetime import datetime
from flask import flash, request, redirect, url_for
from flask_login import login_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from apps import db, bcrypt
from apps.authentication.models import Account


def redirect_url(url, **kwargs):
    """redirect url for functions"""
    return redirect(url_for(url, **kwargs))


def sign_up(form):
    """sign up functions"""

    if form.validate_on_submit():
        create_user = Account(
            email=form.email_address.data,
            role=form.role.data,
            password_hash=generate_password_hash(
                form.password1.data, method='sha256')
        )

        db.session.add(create_user)
        db.session.commit()
        # login_user(create_user)
        flash('Successfully created account!', category='success')

    if form.errors != {}:  # check if any error in validation
        for err_msg in form.errors.values():
            flash(
                f'There was an error with creating a new user: {err_msg}', category='danger')


def sign_in(form):
    """sign in function"""
    attempted_email = form.email_address.data
    attempted_password = form.password.data
    attempted_user = Account.query.filter_by(
        email=attempted_email).first()
    email = ['dimas@gooddreamer.id', 'subur@gooddreamer.id']

    if attempted_user and attempted_user.email in email:
        check_pwdhash = bcrypt.check_password_hash(
            attempted_user.password_hash, attempted_password.encode('utf-8'))

        if check_pwdhash:
            if form.check.data:
                login_user(attempted_user, remember=True)
                flash(
                    f'Hai {attempted_user.email}. You has successfully sign in!', category='success')
            else:
                login_user(attempted_user, remember=False)
                flash(
                    f'hai {attempted_user.email}. You has successfully sign in!', category='success')
        else:
            flash('Wrong password!, please try again.', category='danger')
    else:
        flash('Wrong email address!, please try again.', category='danger')
