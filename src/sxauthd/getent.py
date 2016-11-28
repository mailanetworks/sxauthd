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

import grp
import pwd
import threading


# Python has a global interpreter lock, but can the C implementations
# be executed on multiple threads at once? What if greenlets are used?
# Better use locks when calling libc functions that are not thread-safe
getgrnam_lock = threading.Lock()
getpwnam_lock = threading.Lock()
getgrgid_lock = threading.Lock()


class User:
    def __init__(self, username):
        with getpwnam_lock:
            u = pwd.getpwnam(username)
        self.name = u.pw_name
        self.fullname = u.pw_gecos.split(",")[0]
        with getgrgid_lock:
            g = grp.getgrgid(u.pw_gid)
        self.group = g.gr_name

    def __repr__(self):
        return ("<name=%r, fullname=%r, group=%r>" %
                (self.name, self.fullname, self.group))


# subclassing set/frozenset doesn't work
class ImmutableGroup:
    def __init__(self, groupname):
        with getgrnam_lock:
            group = grp.getgrnam(groupname)
        self.name = group.gr_name
        self.members = frozenset(group.gr_mem)

    def __contains__(self, item):
        if isinstance(item, User):
            # the user is usually not listed as member of its primary group
            # so check the primary group first
            return item.group == self.name or item.name in self.members
        raise TypeError("not a User type: %r" % type(item))

    def __repr__(self):
        return ("<members=%r>" % self.members)
