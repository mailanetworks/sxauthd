#!/bin/bash
set -e
if [ "$#" -ne 1 -a "$#" -ne 2 ]; then
    echo "Usage: $0 </destination/path> [/path/to/etc/sxserver]"
    exit 1
fi

if [ $(id -u) -ne 0 ]; then
    echo "Must be run as root"
    exit 2
fi

SELFDIR=$(dirname $(readlink -f "$0"))
DEST="$1"
SXSERVERDIR=${2:-/etc/sxserver/}

is_debian() {
    test -f /etc/debian_version
}

is_redhat() {
    test -f /etc/redhat-release
}

echo -n "Checking for Python ... "
if python2.7 --version; then
    EGG=$SELFDIR/sxauthd-*-py2.7.egg
elif python2.6 --version; then
    EGG=$SELFDIR/sxauthd-*-py2.6.egg
else
    echo "Unable to find Python 2.6 or 2.7"
    exit 1
fi
