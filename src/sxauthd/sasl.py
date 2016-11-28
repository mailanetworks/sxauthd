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
import struct
import string
from flask import current_app
import api


def sasl_auth(username, password):
    username = api.utf8(username).rstrip()
    if not all(c in string.printable for c in username):
        return 'NO', 'username contains non-printable characters', None
    mux = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    mux.connect(current_app.config['SASLAUTHD_MUX'])

    service = current_app.config['SASLAUTHD_SERVICE']
    packet = bytearray()
    for s in [username, password, service, '']:
        packet += struct.pack('>H', len(s))
        packet += bytearray(s, 'utf-8')

    mux.send(packet)
    r = mux.recv(2)
    (n,) = struct.unpack('>H', r)
    r = mux.recv(n)
    code, msg0, msg = r.partition(' ')
    current_app.logger.info('Auth returned %s (%s) %s' % (code, msg0, msg))
    mux.close()
    return code, msg, username
