#!/bin/sh
set -e
set -x
./dist.sh
#cp examples/saslauthd-pam-shadow/Dockerfile .
#sudo docker build -t sxauthd-test-pam .
#cp examples/saslauthd-pam-debian/Dockerfile .
#sudo docker build -t sxauthd-test-pam-debian .
#cp examples/ldap-server/Dockerfile .
#sudo docker build -t test-ldap-server .
#cp examples/ldap-client/Dockerfile .
#sudo docker build -t test-ldap-client .
#cp examples/saslauthd-ldap/Dockerfile .
#sudo docker build -t sxauthd-test-ldap .

cp examples/imap-sxauthd/Dockerfile .
sudo docker build -t sxauthd-imap

sudo docker rm -f ldap-server || true
sudo docker rm -f ldap-client || true
sudo docker run -d  -v /dev/log:/dev/log --name ldap-server --hostname=ldap.example.com test-ldap-server
#sudo docker run -d --name ldap-client --link ldap-server:ldap.example.com test-ldap-client

sudo docker rm -f sxauthd-testing-ldap || true
SX_CLUSTER_PORT=443
SX_NODE_IP=`hostname -I | cut -f1 -d\ `
sudo docker run -p $SX_CLUSTER_PORT:$SX_CLUSTER_PORT --name='sxauthd-testing-ldap'\
    --link ldap-server:ldap.example.com \
    -e SX_NODE_IP=$SX_NODE_IP\
    -e SX_CLUSTER_NAME="`hostname --fqdn`"\
    -e SX_CLUSTER_PORT=$SX_CLUSTER_PORT\
    sxauthd-test-ldap
exit 0



#sudo docker rm -f sxauthd-testing || true
#sudo docker rm -f sxauthd-testing-debian || true
#sudo docker rm -f sxauthd-testing-2fa || true

SX_CLUSTER_PORT=443
#sudo docker run -p $SX_CLUSTER_PORT:$SX_CLUSTER_PORT --name='sxauthd-testing'\
#    -e SX_NODE_IP=$SX_NODE_IP\
#    -e SX_CLUSTER_NAME="`hostname --fqdn`"\
#    -e SX_CLUSTER_PORT=$SX_CLUSTER_PORT\
#    -v /dev/log:/dev/log\
#    sxauthd-test-pam

SX_CLUSTER_PORT=443
# SYS_PTRACE needed by start-stop-daemon
sudo docker run --cap-add SYS_PTRACE -t -p $SX_CLUSTER_PORT:$SX_CLUSTER_PORT --name='sxauthd-testing-debian'\
    -e SX_NODE_IP=$SX_NODE_IP\
    -e SX_CLUSTER_NAME="`hostname --fqdn`"\
    -e SX_CLUSTER_PORT=$SX_CLUSTER_PORT\
    -v /dev/log:/dev/log\
    sxauthd-test-pam-debian
