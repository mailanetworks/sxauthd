##########################################################################
#  Copyright (c) 2015-2016, Skylable Ltd. <info-copyright@skylable.com>  #
#  All rights reserved.                                                  #
#                                                                        #
#  Redistribution and use in source and binary forms, with or without    #
#  modification, are permitted provided that the following conditions    #
#  are met:                                                              #
#                                                                        #
#  1. Redistributions of source code must retain the above copyright     #
#  notice, this list of conditions and the following disclaimer.         #
#                                                                        #
#  2. Redistributions in binary form must reproduce the above            #
#  copyright notice, this list of conditions and the following           #
#  disclaimer in the documentation and/or other materials provided       #
#  with the distribution.                                                #
#                                                                        #
#  3. Neither the name of the copyright holder nor the names of its      #
#  contributors may be used to endorse or promote products derived       #
#  from this software without specific prior written permission.         #
#                                                                        #
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS   #
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT     #
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS     #
#  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE        #
#  COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,            #
#  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES    #
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR    #
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)    #
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,   #
#  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)         #
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED   #
#  OF THE POSSIBILITY OF SUCH DAMAGE.                                    #
##########################################################################

from __future__ import division, absolute_import
from flask import request, session, abort, flash, redirect, \
    url_for, render_template, Blueprint, g, current_app, make_response
from wtforms import Form, TextField, HiddenField, PasswordField, validators
from requests import ConnectionError
from sxauthd.sasl import sasl_auth
from sxauthd.api import handle_create
from sxauthd.sx import SXException
import uuid

browser = Blueprint("browser", __name__)


def debug(msg):
    current_app.logger.debug(msg)


def redirect_to_login(msg):
    session.clear()
    flash(msg)
    debug('redirecting to login page (%s)' % msg)
    return redirect(url_for('browser.login'))


@browser.before_request
def before_request():
    logged_in = session.get('logged_in')
    username = session.get('username')
    debug("logged_in from: %r, username: %r" % (logged_in, username))
    if logged_in is None:
        login_url = url_for("browser.login")
        if request.path == url_for("browser.show_entries"):
            session.clear()
            return redirect(login_url)
        if request.path != login_url:
            abort(403)
    else:
        if logged_in != request.remote_addr:
            return redirect_to_login("Session invalid, login again")
        setattr(g, 'username', username)


class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=1, max=62)])
    password = PasswordField('Password')


@browser.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        code, error, username = sasl_auth(username, form.password.data)
        if code == 'OK':
            session.clear()
            session['logged_in'] = request.remote_addr
            session['username'] = username
            flash('Login successful')
            return redirect(url_for('browser.show_entries'))
    else:
        flash('Please login')
    return render_template('login.html', error=error, form=form)


@browser.route('/logout')
def logout():
    debug("logout")
    return redirect_to_login("You were logged out")


class DeviceForm(Form):
    display = TextField('Device name', [validators.Length(min=1, max=1024)])
    unique = HiddenField([validators.Length(min=36, max=36)])


@browser.route('/')
def show_entries():
    cookie_name = current_app.config['SESSION_COOKIE_NAME'] + '-uuid'
    defaultid = request.cookies.get(cookie_name, str(uuid.uuid4()))
    form = DeviceForm(request.form, unique=defaultid)
    r = make_response(render_template('default.html', form=form))
    path = current_app.config['APPLICATION_ROOT']
    r.set_cookie(cookie_name, defaultid, path=path, max_age=31536000)
    return r


@browser.route("/create", methods=['POST'])
def create():
    form = DeviceForm(request.form)
    if not form.validate():
        current_app.logger.info('bad request')
        return render_template('default.html', form=form), 400
    try:
        url = handle_create(request)
        return render_template('redirect.html', url=url)
    except SXException as e:
        current_app.logger.exception(e)
        flash(str(e))
        return render_template('default.html', form=form), 400
    except ConnectionError as e:
        current_app.logger.exception(e)
        msg = 'Error connecting to SX cluster'
        flash(msg)
        return render_template('default.html', form=form), 502
