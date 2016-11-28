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

import socket

SX_DEFAULT_VOLUME_SIZE = 100*2**30
SX_DEFAULT_REPLICA_COUNT = 1
SX_DEFAULT_MAX_REVISIONS = 1

SX_CLUSTER_PORT = 443
SX_CLUSTER_SSL = True

SX_CLUSTER_INTERNAL_IP = None
SX_CLUSTER_NAME = None
SX_CLUSTER_EXTERNAL_IP = None
SX_CLUSTER_TOKEN = None

# SASL settings

SASLAUTHD_MUX = '/var/run/saslauthd/mux'
SASLAUTHD_SERVICE = 'sxauthd'

# sxauthd settings

LOGINREALM = socket.getfqdn()
APPLICATION_ROOT = '/.auth/'
SX_USER_PREFIX = 'u:'
SX_CLONE_PREFIX = 'd:'

# webapp settings
SESSION_COOKIE_NAME = 'sxauthd'
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = True
PREFERRED_URL_SCHEME = 'https'
JSON_AS_ASCII = False

# Setting this to True allows remote code execution, DON'T
DEBUG = False
