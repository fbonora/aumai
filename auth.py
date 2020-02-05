from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from .form_validator import LoginForm
from .models import User
from .utility import is_admin, is_cassiere, is_operator, is_responsabile_negozio

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None or user.password != form.password.data:
            current_app.logger.error('Utente non riconosciuto {}'.format(form.name.data))
            flash(u'Utente non riconosciuto {}'.format(form.name.data), 'error')
            return redirect(url_for('main.index'))

        current_app.logger.debug('Utente : {}'.format(user.name))
        login_user(user)
        session.permanent = True
        current_app.logger.debug('login done')
        if is_admin(user):
            return redirect(url_for('main.home_admin', panel='utenti'))
        if is_cassiere(user):
            return redirect(url_for('cassiere.home_cassiere', panel='versamenti'))
        if is_operator(user):
            return redirect(url_for('main.index'))
        if is_responsabile_negozio(user):
            return redirect(url_for('responsabile.home_responsabile', panel='versamenti'))
    else:
        return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
