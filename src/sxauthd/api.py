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
from flask import current_app, request, redirect, Blueprint, g, jsonify
import os
import base64
import binascii
from sxauthd.sasl import sasl_auth
from sxauthd.sx import SXCluster, SXException
import uuid
import urllib
import urlparse
import re

api = Blueprint('api', __name__)


def utf8(s):
    if s is None:
        return None
    if isinstance(s, str) or isinstance(s, unicode):
        return s.encode('utf-8')
    return bytearray(s)


def debug(msg):
    current_app.logger.debug(msg)


def unauthenticated(msg):
    r = jsonify({'ErrorMessage': 'Authentication failed',
                 'ErrorDetails': msg,
                 'NodeId': 'SXAUTHD'})
    r.status_code = 401
    r.www_authenticate.realm = current_app.config['LOGINREALM']
    return r


def bad_request():
    r = jsonify({'ErrorMessage': 'Bad API request',
                 'ErrorDetails': 'Expected a "display" and "unique" fields',
                 'NodeId': 'SXAUTHD'})
    r.status_code = 400
    return r


@api.before_request
def before_request():
    auth = request.authorization
    current_app.logger.info("Got request: %s" % request.data)
    if not auth:
        current_app.logger.info("No credentials: %s, %s" % (request.__dict__, request.headers))
        return unauthenticated('No credentials provided')
    code, msg, username = sasl_auth(auth.username, auth.password)
    if code == 'OK':
        setattr(g, 'username', username)
    else:
        current_app.logger.info("Failed to auth: %s" % msg)
        return unauthenticated(msg)


def get_sx():
    sx = getattr(g, 'sx', None)
    if sx is None:
        sx = SXCluster(current_app.config['SX_CLUSTER_INTERNAL_IP'],
                       current_app.config['SX_CLUSTER_PORT'],
                       current_app.config['SX_CLUSTER_SSL'],
                       current_app.config['SX_CLUSTER_TOKEN'],
                       current_app.config['SX_CLUSTER_NAME'])
        debug('created SX instance')
        setattr(g, 'sx', sx)
    return sx


sanitize_re = re.compile("[^A-Za-z0-9-._~:]")


def get_username():
    return sanitize_re.sub("_", getattr(g, 'username', None))


def ensure_exists(sx, head_url, put_url, payload, what):
    debug("Checking for existence of %s" % what)
    if sx.head(head_url).status_code == 200:
        debug("%s already exists" % what)
    else:
        debug("Creating %s" % what)
        try:
            sx.job_put(put_url, payload, 'create ' + what).poll_wait()
            current_app.logger.info("Created %s" % what)
        except SXException as e:
            debug("Failed to create %s: %s" % (what, str(e)))
            # maybe there was a race condition and it already exists
            if sx.head(head_url).status_code == 200:
                debug("%s already exists" % what)
                return
            pass


def ensure_user_exists(sx, username, existing=None, full=None):
    payload = {'userName': username,
               'userKey': binascii.hexlify(os.urandom(20)),
               'userType': 'normal'
               }
    if existing is not None:
        payload.update({'existingName': existing})
        what = 'user %s clone of %s' % (username, existing)
    else:
        what = 'user %s' % username
    if full is not None:
        payload.update({'userDesc': full})

    ensure_exists(sx, '.users/%s' % username, '/.users', payload, what)


def get_userkey(sx, username):
    debug('retrieving token for user %s' % username)
    r = sx.get('/.users/%s' % username)
    if r.status_code != 200:
        raise SXException(r.text)
    info = r.json()
    uid = info['userID']
    key = info['userKey']
    tokenbin = binascii.unhexlify(uid) + binascii.unhexlify(key) + '\x00\x00'
    return base64.b64encode(tokenbin)


def ensure_volume_exists(sx, owner, volume):
    payload = {'volumeSize': current_app.config['SX_DEFAULT_VOLUME_SIZE'],
               'owner': owner,
               'replicaCount': current_app.config['SX_DEFAULT_REPLICA_COUNT'],
               'maxRevisions': current_app.config['SX_DEFAULT_MAX_REVISIONS'],
               }
    volurl = '/%s' % volume
    ensure_exists(sx, volurl + '?o=locate', volurl,
                  payload, 'volume %s' % volume)


def handle_create(request):
    display = utf8(request.form.get('display'))
    unique = utf8(request.form.get('unique', type=str))
    debug('Request from %r at %s, display=%r, unique=%r' %
          (request.user_agent, request.remote_addr, display, unique))
    if (display is None) or (unique is None):
        return
    if (len(display) <= 1) or (len(unique) <= 1):
        return
    sx = get_sx()
    raw_username = get_username()
    username = current_app.config['SX_USER_PREFIX'] + raw_username
    ensure_user_exists(sx, username, full=raw_username)
    volume = username
    if sx.head('/%s?o=locate' % volume).status_code != 200:
        ensure_volume_exists(sx, username, volume)
    clustername = current_app.config['SX_CLUSTER_NAME']
    # deterministic id generation
    debug('generating uuid from %r, %r, %r' % (clustername, unique, username))
    ns_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, clustername)
    device = uuid.uuid5(ns_uuid, unique)
    clone = uuid.uuid5(device, utf8(username))
    # SX rejects username with / in them: use filename-safe base64 encoding
    cloneb64 = base64.b64encode(clone.bytes, '-_').strip('=')
    clonename = current_app.config['SX_CLONE_PREFIX'] + cloneb64
    full = str(display)
    ensure_user_exists(sx, clonename, existing=username, full=full)
    token = get_userkey(sx, clonename)
    port = current_app.config['SX_CLUSTER_PORT']
    ssl = current_app.config['SX_CLUSTER_SSL']
    platform = request.user_agent.platform
    if platform == 'ipad' or platform == 'iphone':
        url = "sx://%s;token=%s,ip=%s,port=%d,ssl=%c" % (
              clustername,
              urllib.quote(token, safe=''),
              current_app.config['SX_CLUSTER_EXTERNAL_IP'],
              port,
              ssl and 'y' or 'n'
            )
    else:
        # SXDrive/Qt
        query = urllib.urlencode({
            'token': token,
            'ip': current_app.config['SX_CLUSTER_EXTERNAL_IP'],
            'port': port,
            'ssl': ssl and 'y' or 'n'
            })
        url = urlparse.urlunparse(('sx', clustername, '/', None, query, None))
    current_app.logger.info('Returning token for %s (%s)' %
                            (clonename, username))
    return url


@api.route("/v1/create", methods=['POST'])
def create():
    url = handle_create(request)
    if url is None:
        current_app.logger.warning('bad request')
        return bad_request()
    return redirect(url)
