#!/bin/sh
set -e
. $(dirname "$0")/sxauthd_common.sh
USER=$(stat -c '%U' "$DEST")
GROUP="nobody"
INI="$DEST/sxauthd.ini"

echo Installing/upgrading ${EGG} in "$DEST"
/usr/lib/python2.6/vendor-packages/easy_install ${EGG}

echo
UWSGI_SOCKET=$(grep uwsgi_pass $SXSERVERDIR/sxhttpd.conf |grep -Po '(?<=unix://).*(?=;)')

echo "Configuring $INI with user:group = $USER:$GROUP and socket at $UWSGI_SOCKET"
cat >"$INI" <<EOF
[uwsgi]
master = true
die-on-term = true
pidfile = /var/run/uwsgi-sxauthd.pid
socket = $UWSGI_SOCKET
chmod-socket = 660
chown-socket = $USER:$GROUP
uid = $USER
gid = $GROUP
module = sxauthd:app
processes = 8
threads = 4
chdir = /srv/sxauthd/
env = SXAUTHD_SETTINGS=$DEST/config.py
EOF

echo "Copying init script"
sed -e "s|/srv/sxauthd/|$DEST/|" $SELFDIR/sxauthd.init >/etc/init.d/sxauthd
chmod +x /etc/init.d/sxauthd
