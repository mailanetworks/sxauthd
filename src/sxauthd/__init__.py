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
from flask import Flask, g, jsonify
from hashlib import sha256
from requests import ConnectionError
import hmac
import sxauthd.config
from sxauthd.api import api
from sxauthd.browser import browser
from sxauthd.sx import SXException, SXJobError
import sys

app = Flask(__name__, static_path='/.auth/static')
# set default values
app.config.from_object(sxauthd.config)
# override with user config
app.config.from_envvar('SXAUTHD_SETTINGS')

if not app.debug:
    import logging
    stderr = logging.StreamHandler()
    stderr.setLevel(logging.DEBUG)
    app.logger.addHandler(stderr)
    logger = logging.getLogger(app.logger_name)
    logger.setLevel(logging.DEBUG)

requires = ['SX_CLUSTER_NAME', 'SX_CLUSTER_EXTERNAL_IP',
            'SX_CLUSTER_INTERNAL_IP', 'SX_CLUSTER_TOKEN']
missing = [x for x in requires if app.config[x] is None]

if missing != []:
    app.logger.error("You must set at least the following config values: %r" %
                     missing)
    sys.exit(10)


secret_key = hmac.new(app.config['SX_CLUSTER_TOKEN'],
                      'sxauthd_cookie_key\x01', sha256).digest()
app.config.update({'SECRET_KEY': secret_key})


root = app.config['APPLICATION_ROOT']
app.register_blueprint(api, url_prefix=(root + "api"))
app.register_blueprint(browser, url_prefix=(root + "web"),
                       static_url_path=root+"static")
app.logger.info('Configured to connect to SX cluster %s' %
                app.config['SX_CLUSTER_NAME'])
app.logger.info('Connecting to cluster internally at http%s://%s:%d' % (
                app.config['SX_CLUSTER_SSL'] and 's' or '',
                app.config['SX_CLUSTER_INTERNAL_IP'],
                app.config['SX_CLUSTER_PORT']))
app.logger.info('Connecting to cluster externally at http%s//%s:%d' % (
                app.config['SX_CLUSTER_SSL'] and 's' or '',
                app.config['SX_CLUSTER_EXTERNAL_IP'],
                app.config['SX_CLUSTER_PORT']))


@app.errorhandler(SXJobError)
def handle_job_error(error):
    app.logger.exception(error)
    response = jsonify(error.to_dict())
    response.status_code = 400
    return response


@app.errorhandler(SXException)
def handle_sx_exception(error):
    app.logger.exception(error)
    response = jsonify(error.to_dict())
    response.status_code = 500
    return response


@app.errorhandler(ConnectionError)
def handle_conn_error(error):
    app.logger.exception(error)
    try:
        s = str(error)
    except Exception:
        s = error.args
    response = jsonify({'ErrorMessage': 'Error connecting to SX cluster',
                        'ErrorDetails': s,
                        'NodeId': 'SXAUTHD'})
    response.status_code = 502
    return response


@app.teardown_appcontext
def teardown(exception):
    sx = getattr(g, 'sx', None)
    if sx is not None:
        app.logger.debug('closing SX instance')
        sx.close()
