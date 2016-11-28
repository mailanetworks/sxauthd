FROM debian:jessie
ENV http_proxy http://proxy:3128

# Install newer SX
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
            build-essential libltdl-dev libtool libfcgi-dev libyajl-dev libcurl4-openssl-dev libssl-dev \
            git nginx && \
    apt-get clean
RUN git clone http://git.skylable.com/sx
WORKDIR sx
RUN git pull && ./configure --disable-sxhttpd --prefix=/usr \
    --localstatedir=/var --sysconfdir=/etc
RUN make -j 10 && make install -s

# Install sxauthd dependencies
RUN apt-get install -y --no-install-recommends python-dev virtualenv uwsgi uwsgi-plugin-python sasl2-bin && \
    apt-get clean
# Setup virtualenv for sxauthd
RUN mkdir /srv/sxauthd && \
    chown www-data:www-data /srv/sxauthd
USER www-data
RUN virtualenv /srv/sxauthd
COPY src/dist/*.egg /tmp/
RUN . /srv/sxauthd/bin/activate && \
    easy_install /tmp/*.egg
COPY sxauthd.ini /etc/uwsgi/apps-enabled/

USER root
COPY demo-debian.sh /root/
RUN sed -i -e 's/START=no/START=yes/' /etc/default/saslauthd

USER root
EXPOSE 443
CMD ["/bin/bash","-c","set -e && /root/demo-debian.sh"]
