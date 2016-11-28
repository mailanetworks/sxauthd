FROM centos:7

RUN echo 'deltarpm=0' >> /etc/yum.conf && \
    sed -i 's/^mirrorlist=/#mirrorlist=/' /etc/yum.repos.d/* && \
    sed -i 's/^#baseurl=/baseurl=/' /etc/yum.repos.d/* && \
    sed -i 's/enabled=1/enabled=0/' /etc/yum/pluginconf.d/fastestmirror.conf && \
    yum install -y epel-release && yum clean all
# Install newer SX
RUN yum install -y nginx gcc git && yum clean all
RUN git clone http://git.skylable.com/sx
RUN yum install -y libtool-ltdl-devel libtool yajl-devel 'pkgconfig(libidn)' \
    'pkgconfig(libcrypto)' 'pkgconfig(openssl)' 'zlib-devel' 'pkgconfig(nss)' \
    make && \
    yum clean all
WORKDIR sx
RUN git pull && ./configure --disable-sxhttpd --prefix=/usr \
    --localstatedir=/var --sysconfdir=/etc --with-nss
RUN make -j 10 && make install -s

# Install sxauthd
RUN yum install -y epel-release && \
    yum install -y python-pip python-setuptools python-virtualenv cyrus-sasl && \
    yum clean all

# Setup virtualenv for sxauthd
RUN mkdir /srv/sxauthd && \
    chown nobody:nobody /srv/sxauthd
USER nobody
RUN virtualenv /srv/sxauthd && \
    . /srv/sxauthd/bin/activate && \
    pip install uwsgi
# Istall sxauthd binary distribution
COPY src/dist/*.egg /tmp/
RUN . /srv/sxauthd/bin/activate && \
    easy_install /tmp/*.egg

USER root
COPY demo-ldap.sh /root/demo.sh

EXPOSE 443
USER root
CMD ["/bin/bash","-c","set -e && /root/demo.sh"]
