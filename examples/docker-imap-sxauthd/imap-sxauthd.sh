#!/bin/sh
set -e
set -o nounset

# One-time setup for sxauthd
cat >/srv/sxauthd/config.py <<EOF
SX_CLUSTER_INTERNAL_IP="$SX_CLUSTER_INTERNAL_IP"
SX_CLUSTER_EXTERNAL_IP="$SX_CLUSTER_EXTERNAL_IP"
SX_CLUSTER_TOKEN="$(cat /root/.sx/$SX_CLUSTER_NAME/auth/admin)"
SX_CLUSTER_NAME="$SX_CLUSTER_NAME"
SX_CLUSTER_PORT=$SX_CLUSTER_PORT
EOF

# Start sxauthd
adduser www-data sasl
service saslauthd start

/usr/bin/uwsgi --ini /etc/uwsgi/apps-enabled/sxauthd.ini
