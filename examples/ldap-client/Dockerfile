FROM centos:6

RUN echo 'deltarpm=0' >> /etc/yum.conf && \
    sed -i 's/^mirrorlist=/#mirrorlist=/' /etc/yum.repos.d/* && \
    sed -i 's/^#baseurl=/baseurl=/' /etc/yum.repos.d/* && \
    sed -i 's/enabled=1/enabled=0/' /etc/yum/pluginconf.d/fastestmirror.conf && \
    yum install -y authconfig pam_ldap openldap openldap-clients sssd && yum clean all

RUN /usr/sbin/authconfig --enableldapauth --ldapserver=ldap://ldap.example.com --ldapbasedn="dc=example,dc=com" --update
COPY sssd.conf /etc/sssd/
RUN sed -i -re 's/(passwd|shadow|group).*:.*/\1: files sss/' /etc/nsswitch.conf && \
    chmod 0600 /etc/sssd/sssd.conf

EXPOSE 389
CMD ["/bin/bash","-c","set -e && /sbin/service sssd start && while true; do sleep 60000; done"]
