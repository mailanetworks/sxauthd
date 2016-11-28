#!/bin/bash
set -e
. $(dirname "$0")/sxauthd_common.sh

SXSETUP_CONF=${SXSERVERDIR}/sxsetup.conf
UWSGI_SOCKET="/var/run/uwsgi-sxauthd.socket"

USER="nobody"
GROUP="nobody"
SASLAUTHD_CONF="/etc/saslauthd"

echo -n "Checking for presence of sxsetup.conf ... "
test -f "$SXSETUP_CONF" || {
    echo "Unable to find $SXSETUP_CONF"
    exit 1
}
echo "$SXSETUP_CONF"

echo "Installing dependencies for $EGG to $DEST"
mkdir -p "$DEST"
chown "$USER":"$GROUP" "$DEST"

# should use virtualenv but it didn't work:
# ERROR: The executable /srv/sxauthd/bin/python2.6 is not functioning
# ERROR: It thinks sys.prefix is u'/root/sxauthd' (should be u'/srv/sxauthd')
# ERROR: virtualenv is not compatible with this system or executable
/usr/lib/python2.6/vendor-packages/easy_install pip
pip install uwsgi
pip install -r requirements.txt

cp -v $SELFDIR/uwsgi_params $SXSERVERDIR/

echo "Loading sxsetup.conf from $SXSETUP_CONF"
. "$SXSETUP_CONF"

if [ -z "$SX_NODE_INTERNAL_IP" ]; then
    SX_NODE_INTERNAL_IP="$SX_NODE_IP"
fi

if [ "$SX_USE_SSL" != "yes" ]; then
    echo "The SX cluster must have SSL enabled!"
    exit 3
fi

echo "Generating $DEST/config.py"
cat >"$DEST/config.py" <<EOF
SX_CLUSTER_INTERNAL_IP="$SX_NODE_INTERNAL_IP"
SX_CLUSTER_EXTERNAL_IP="$SX_NODE_IP"
SX_CLUSTER_PORT=$SX_PORT
SX_CLUSTER_NAME="$SX_CLUSTER_NAME"
SX_CLUSTER_TOKEN="$(sxadm node --info ${SX_DATA_DIR} | grep Admin | cut -f3 -d\ )"
EOF

echo "Updating sxhttpd configuration to enable sxauthd"
cp -v "$SXSERVERDIR/sxhttpd.conf" "$SXSERVERDIR/sxhttpd.conf.bak.$(date +%s)"

grep 'location /.auth' "$SXSERVERDIR"/sxhttpd.conf >/dev/null || sed -i -e "s|location /.errors|location /.auth {\n\
                 include $SXSERVERDIR/uwsgi_params;\n\
                 uwsgi_pass unix://$UWSGI_SOCKET;\n\
             }\n             \0|" "$SXSERVERDIR"/sxhttpd.conf

echo "Configuring saslauthd"

cat >/etc/saslauthd.conf <<EOF
ldap_servers: ldap://ldap.example.com
ldap_search_base: dc=example,dc=com
ldap_filter: (&(uid=%u)(objectClass=person))
EOF

$SELFDIR/sxauthd_upgrade_omnios.sh "$1" "$2"

echo
echo "Customize /etc/saslauthd.conf according to your LDAP configuration"
echo See /usr/share/doc/cyrus-sasl*/LDAP_SASLAUTHD*
