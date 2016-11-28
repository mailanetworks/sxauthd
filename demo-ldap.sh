#!/bin/sh
set -e

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
SX_SSL_KEY_FILE=/etc/pki/tls/private/sx.key
SX_SSL_CERT_FILE=/etc/pki/tls/certs/sx.pem
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
    uwsgi_pass unix:\/\/\/tmp\/uwsgi.socket;\n\
}\n\0/' /etc/sxserver/sxhttpd.conf
/usr/sbin/sxserver restart

# Start sxauthd
# Note: you don't have to specify ldap_bind_dn and ldap_password
# if your LDAP server allows anonymous searches
cat >/etc/saslauthd.conf <<EOF
ldap_servers: ldap://ldap.example.com
ldap_search_base: dc=example,dc=com
ldap_filter: (&(uid=%u)(objectClass=person))
EOF

# direct bind without prior search:
#cat >/etc/saslauthd.conf <<EOF
#ldap_servers: ldap://ldap.example.com
#ldap_auth_method: fastbind
#ldap_filter: uid=%u,ou=people,dc=example,dc=com
#EOF

#ldap_bind_dn: cn=Manager,dc=example,dc=com
#ldap_password: testrootpassword
/usr/sbin/saslauthd -m /run/saslauthd -a ldap -O /etc/saslauthd.conf

unset http_proxy
unset HTTP_PROXY
unset https_proxy
unset HTTPS_PROXY

su nobody -s /bin/sh -c '. /srv/sxauthd/bin/activate &&  \
uwsgi --socket /tmp/uwsgi.socket --uid nobody --gid nobody -H /srv/sxauthd -w sxauthd:app --master \
    --env SXAUTHD_SETTINGS=/srv/sxauthd/config.py \
    --processes 8 --threads 4'
