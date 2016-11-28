FROM centos:6

RUN echo 'deltarpm=0' >> /etc/yum.conf && \
    sed -i 's/^mirrorlist=/#mirrorlist=/' /etc/yum.repos.d/* && \
    sed -i 's/^#baseurl=/baseurl=/' /etc/yum.repos.d/* && \
    sed -i 's/enabled=1/enabled=0/' /etc/yum/pluginconf.d/fastestmirror.conf && \
    printf '\
[skylable]\n\
name=Skylable\n\
baseurl=http://cdn.skylable.com/centos/$releasever/$basearch/\n\
gpgcheck=0' >/etc/yum.repos.d/skylable.repo && \
    yum install -y skylable-sx rsyslog tar && yum clean all
# Unpack and install dependencies
COPY dist/skylable-centos.repo /etc/yum.repos.d/skylable.repo
RUN yum install -y epel-release && \
    yum install -y skylable-sx python-pip python-setuptools python-virtualenv \
                   cyrus-sasl gcc && \
    yum clean all
WORKDIR /root
COPY sxauthd-0.4.tar.gz /root/
COPY demo-ldap-6.sh /root/demo.sh

EXPOSE 443
USER root
CMD ["/bin/bash","-c","set -e && /root/demo.sh"]
