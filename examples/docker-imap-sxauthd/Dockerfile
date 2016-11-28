FROM debian:jessie

# Install sxauthd dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential python-dev virtualenv uwsgi uwsgi-plugin-python sasl2-bin && \
    apt-get clean
# Setup virtualenv for sxauthd
RUN mkdir /srv/sxauthd && \
    chown www-data:www-data /srv/sxauthd
USER www-data
RUN virtualenv /srv/sxauthd
COPY saslauthd /etc/default/saslauthd
#COPY requirements.txt /tmp/
#RUN su - nobody -s /bin/bash -c "virtualenv --no-pip /srv/sxauthd && \
#        export HOME=/srv/sxauthd && \
#        . /srv/sxauthd/bin/activate && \
#        easy_install pip &&
#        pip install uwsgi && \
#"
COPY *.egg /tmp/
RUN . /srv/sxauthd/bin/activate && \
    easy_install /tmp/*.egg
COPY sxauthd.ini /etc/uwsgi/apps-enabled/

USER root
COPY imap-sxauthd.sh /root/
RUN sed -i -e 's/START=no/START=yes/' /etc/default/saslauthd

USER root
EXPOSE 10000
CMD ["/bin/bash","-c","set -e && /root/imap-sxauthd.sh"]
