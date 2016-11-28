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
from requests.auth import AuthBase
from requests import Session
from email.utils import formatdate
from hashlib import sha1
import hmac
from urlparse import urlunsplit
from time import sleep, time
import json
import base64


class SXException(Exception):
    def __init__(self, details,
                 message='Error communicating with SX cluster'):
        Exception.__init__(self)
        self.details = details
        self.message = message

    def to_dict(self):
        return {'ErrorMessage': self.message,
                'ErrorDetails': self.details,
                'NodeId': 'SXAUTHD'}

    def __str__(self):
        return "%s: %s" % (self.message, self.details)


class SXAuth(AuthBase):
    """Attaches SX Authorization header to the given Request object."""
    def __init__(self, token, clustername):
        binauth = base64.b64decode(token)
        if len(binauth) != 42:
            raise SXException("Invalid SX auth token")
        self.binuid = binauth[:20]
        self.binkey = binauth[20:40]
        self.binpad = binauth[40:42]
        self.clustername = clustername

    def __call__(self, r):
        r.method
        hash = sha1()
        if r.body is not None:
            hash.update(r.body)
        bodyhash = hash.hexdigest()
        date = formatdate(timeval=None, localtime=False, usegmt=True)
        text = '\n'.join([r.method, r.path_url[1:], date, bodyhash]) + '\n'
        digest = hmac.new(self.binkey, text, sha1).digest()
        encsky = base64.b64encode(self.binuid + digest + '\x00\x00').strip()
        r.headers['Authorization'] = 'SKY %s' % encsky
        r.headers['Date'] = date
        r.headers['SX-Cluster-Name'] = self.clustername
        if 'Expect' in r.headers:
            del r.headers['Expect']
        return r


class SXCluster():
    """Makes requests to an SX cluster."""
    def __init__(self, host, port, is_secure, token, clustername):
        self.host = host
        self.port = port
        self.is_secure = is_secure
        self.session = Session()
        self.session.auth = SXAuth(token, clustername)

    def url(self, path, query):
        if self.is_secure:
            scheme = "https"
        else:
            scheme = "http"
        netloc = self.host
        if self.port is not None:
            netloc += ":%d" % self.port
        return urlunsplit((scheme, netloc, path, query, None))

    def check(self, r):
        if r.status_code == 502 or r.status_code == 504:
            raise SXException(r.text, 'Cannot connect to SX cluster')
        if not ('SX-Cluster' in r.headers):
            raise SXException(r.text, 'Not an SX cluster')
        if r.status_code != 200:
            try:
                info = r.json()
                if 'ErrorMessage' in info:
                    raise SXException(info['ErrorMessage'])
            except ValueError:
                pass
        return r

# TODO: SSL cert verif.
    def head(self, path, query=None):
        return self.session.head(self.url(path, query), verify=False)

    def get(self, path, query=None):
        r = self.session.get(self.url(path, query), verify=False)
        return self.check(r)

    def put(self, path, query=None, data=None,
            content_type='application/octet-stream'):
        r = self.session.put(self.url(path, query), data, verify=False,
                             headers={'Content-Type': content_type})
        return self.check(r)

    def delete(self, path, query=None):
        r = self.session.put(self.url(path, query), verify=False)
        return self.check(r)

    def job_put(self, path, payload, desc):
        r = self.put(path, data=json.dumps(payload),
                     content_type='application/json')
        return SXJob(self, r, desc)

    def job_delete(self, path, payload, desc):
        r = self.delete(path)
        return SXJob(self, r, desc)

    def close(self):
        self.session.close()
        self.session = None


class SXJobError(SXException):
    pass


class SXJob():
    """Makes requests to an SX cluster."""
    def __init__(self, cluster, reply, desc):
        self.cluster = cluster
        # TODO: override cluster host based on host we actually sent the query
        try:
            info = reply.json()
        except ValueError:
            raise SXException(reply.text, 'cannot parse JSON')
        if 'ErrorMessage' in info:
            raise SXJobError(info['ErrorMessage'], desc)
        self.requestId = info['requestId']
        self.min_poll = info['minPollInterval']/1000
        self.max_poll = info['maxPollInterval']/1000
        self.poll_interval = self.min_poll
        self.last_poll = time()
        self.desc = desc

    def poll(self):
        delta = time() - self.last_poll
        if delta < self.poll_interval:
            delta = self.poll_interval - max(0, delta)
            # FIXME: grequests integration
            sleep(delta)
        r = self.cluster.get("/.results/%s" % self.requestId)
        info = r.json()
        if info['requestId'] != self.requestId:
            raise SXException("Job requestId mismatch: %s != %d" %
                              (info['requestId'], self.requestId))
        self.poll_interval += self.min_poll
        self.poll_interval = min(self.poll_interval, self.max_poll)
        self.status = info['requestStatus']
        if self.status == 'ERROR':
            message = info['requestMessage']
            raise SXJobError(message, self.desc)
        if self.status == 'OK' or self.status == 'PENDING':
            return self.status
        raise SXException("Unknown job status %s" % self.status)

    def poll_wait(self):
        while self.poll() != 'OK':
            pass
