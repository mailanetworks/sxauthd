# centos:7 doesn't have google-authenticator in epel
# and the version in centos:6 doesn't support forward_pass
FROM debian:jessie
ENV http_proxy http://proxy:3128
ENV https_proxy http://proxy:3128

RUN apt-get update && \
    apt-get install -y --no-install-recommends python-pip python-setuptools nginx gcc \
            build-essential libltdl-dev libtool libfcgi-dev libyajl-dev libcurl4-openssl-dev libssl-dev \
            python-flask git python-requests uwsgi uwsgi-plugin-python \
            sasl2-bin libpam-google-authenticator qrencode && \
    apt-get clean
RUN git clone http://git.skylable.com/sx
WORKDIR sx
RUN git pull && ./configure --disable-sxhttpd --prefix=/usr \
    --localstatedir=/var --sysconfdir=/etc
RUN make -j 10 && make install -s
RUN apt-get install --no-install-recommends -y virtualenv python-wtforms
RUN mkdir /srv/sxauthd && \
    chown www-data:www-data /srv/sxauthd
WORKDIR /tmp/src
COPY src/ /tmp/src/
RUN chown -R www-data:www-data /tmp/src
RUN sed -i -e 's/START=no/START=yes/' /etc/default/saslauthd
USER www-data
RUN virtualenv --system-site-packages /srv/sxauthd/ && \
    . /srv/sxauthd/bin/activate && \
    python setup.py install
COPY setup-2fa.sh /root/setup.sh
COPY start.sh /root/start.sh
COPY sxauthd-debian-2fa /etc/pam.d/sxauthd
COPY sxauthd.deny /etc/
COPY sxauthd.ini /etc/uwsgi/apps-enabled/

USER root
EXPOSE 10443
CMD ["/bin/bash","-c","set -e && /root/start.sh"]
