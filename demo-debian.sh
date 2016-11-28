#!/bin/sh
set -e

# Add example users
useradd test1
useradd test2
printf "password1\npassword1\n" | passwd test1
printf "password2\npassword2\n" | passwd test2

# One-time setup for SX
export SX_CLUSTER_INTERNAL_IP=`hostname -I|cut -f1 -d\ `
export SX_CLUSTER_EXTERNAL_IP=$SX_NODE_IP
cat >cert.conf <<EOF
[ req ]
default_bits		= 2048
distinguished_name	= req_distinguished_name
prompt			= no
encrypt_key		= no
x509_extensions		= v3_ca

[ req_distinguished_name ]
CN		       = $SX_CLUSTER_NAME

[ v3_ca ]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer:always
basicConstraints = critical,CA:true
keyUsage=keyCertSign,cRLSign,digitalSignature,keyEncipherment
EOF
SX_SSL_KEY_FILE=/etc/ssl/private/sx.key
SX_SSL_CERT_FILE=/etc/ssl/certs/sx.pem
openssl req -days 1825 -x509 -config cert.conf -new -keyout $SX_SSL_KEY_FILE -out $SX_SSL_CERT_FILE
cat >/etc/sxserver/sxsetup.conf <<EOF
SX_CLUSTER_NAME="$SX_CLUSTER_NAME"
SX_DATA_DIR="/var/lib/sxserver/storage"
SX_RUN_DIR="/var/run/sxserver"
SX_LIB_DIR="/var/lib/sxserver"
SX_LOG_FILE="/var/log/sxserver/sxfcgi.log"
SX_NODE_SIZE="500G"
SX_NODE_IP="$SX_NODE_IP"
SX_NODE_INTERNAL_IP="$SX_CLUSTER_INTERNAL_IP"
SX_EXISTING_NODE_IP=""
SX_SERVER_USER="nobody"
SX_SERVER_GROUP="nobody"
SX_CHILDREN_NUM="32"
SX_PORT="$SX_CLUSTER_PORT"
SX_USE_SSL="yes"
SX_SSL_KEY_FILE="$SX_SSL_KEY_FILE"
SX_SSL_CERT_FILE="$SX_SSL_CERT_FILE"
SX_CFG_VERSION="2"
SX_CLUSTER_UUID=996e5860-b6b4-4661-a951-150ac5757599
SX_CLUSTER_KEY=CLUSTER/ALLNODE/ROOT/USERwAG2WqlccWihwR/aXaT0VNlAPxoDgAA
EOF
/usr/sbin/sxsetup --config-file /etc/sxserver/sxsetup.conf --wait

# One-time setup for sxauthd

. /etc/sxserver/sxsetup.conf
cat >/srv/sxauthd/config.py <<EOF
SX_CLUSTER_INTERNAL_IP="$SX_NODE_INTERNAL_IP"
SX_CLUSTER_EXTERNAL_IP="$SX_NODE_IP"
SX_CLUSTER_TOKEN="`sxadm node --info /var/lib/sxserver/storage | grep Admin|cut -f3 -d\ `"
SX_CLUSTER_NAME="$SX_CLUSTER_NAME"
SX_CLUSTER_PORT=$SX_CLUSTER_PORT
EOF

sed -i -e 's/location \/.errors/location \/.auth {\n\
    include \/etc\/nginx\/uwsgi_params;\n\
    uwsgi_pass unix:\/\/\/run\/uwsgi\/app\/sxauthd\/socket;\n\
}\n\0/' /etc/sxserver/sxhttpd.conf

# Start sxauthd
adduser www-data sasl
service saslauthd start
service uwsgi start

/usr/sbin/sxserver restart

tail -f /var/log/uwsgi/app/sxauthd.log
