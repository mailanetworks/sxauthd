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

"""SX cluster authentication server

Creates SX cluster users after authenticating via saslauthd.
"""

from setuptools import setup
import os
version = os.getenv("VERSION")

setup(
    name='sxauthd',
    version=version,
    long_description=__doc__,
    packages=['sxauthd'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=["setuptools_git >= 1.1", ],
    install_requires=[
        'Flask>=0.10.1',
        'requests>=2.5.3',
        'WTForms>=2.0.2'
    ],
    author="Skylable Dev Team",
    author_email="dev-team@skylable.com",
    url="http://www.skylable.com/products/",
    description="SX cluster authentication server",
    license="All Rights Reserved",
    platforms=["any"]
)
