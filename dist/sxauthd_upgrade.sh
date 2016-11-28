#!/bin/sh
set -e
. $(dirname "$0")/sxauthd_common.sh
USER=$(stat -c '%U' "$DEST")
if is_debian; then
    GROUP="nogroup"
elif is_redhat; then
    GROUP="nobody"
fi
INI="$DEST/sxauthd.ini"

echo Installing/upgrading ${EGG} in "$DEST"
. "$DEST/bin/activate"
easy_install ${EGG}

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
logger = syslog:uwsgi,daemon
uid = $USER
gid = $GROUP
module = sxauthd:app
processes = 8
threads = 4
virtualenv = $DEST/
env = SXAUTHD_SETTINGS=$DEST/config.py
EOF

echo "Copying init script"
sed -e "s|/srv/sxauthd/|$DEST/|" $SELFDIR/sxauthd.init >/etc/init.d/sxauthd
chmod +x /etc/init.d/sxauthd

echo -n "Start sxauthd on boot by running this command: "
if is_redhat; then
    echo "chkconfig --add sxauthd"
elif is_debian; then
    echo "update-rc.d sxauthd defaults"
fi
