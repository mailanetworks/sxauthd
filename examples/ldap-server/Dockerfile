FROM centos:5

RUN echo 'deltarpm=0' >> /etc/yum.conf && \
    sed -i 's/^mirrorlist=/#mirrorlist=/' /etc/yum.repos.d/* && \
    sed -i 's/^#baseurl=/baseurl=/' /etc/yum.repos.d/* && \
    sed -i 's/enabled=1/enabled=0/' /etc/yum/pluginconf.d/fastestmirror.conf && \
    yum install -y openldap-servers openldap-clients && yum clean all

RUN echo "rootpw `slappasswd -s testrootpassword`" >>/etc/openldap/slapd.conf && \
    echo 'access to attr=userPassword \
          by self write \
          by anonymous auth \
          by dn.base="cn=Manager,dc=example,dc=com" write \
          by * none' >>/etc/openldap/slapd.conf && \
    echo 'access to * \
          by self write \
          by dn.base="cn= Manager,dc=example,dc=com" write \
          by * read' >>/etc/openldap/slapd.conf && \
    sed -i -e 's/my-domain/example/g' /etc/openldap/slapd.conf && \
    cp /etc/openldap/DB_CONFIG.example /var/lib/ldap/DB_CONFIG && \
    chown ldap:ldap /var/lib/ldap/DB_CONFIG
COPY add-user.ldif /root/
COPY init.ldif /root/

EXPOSE 389
CMD ["/bin/bash","-c","set -x && \
    service ldap start && \
    sleep 1 && \
    ldapadd -w testrootpassword -cxD cn=Manager,dc=example,dc=com -f /root/init.ldif && \
    ldapsearch -x -b 'dc=example,dc=com' '(objectclass=*)' && \
    ldapadd -w testrootpassword -cxD cn=Manager,dc=example,dc=com -f /root/add-user.ldif && \
    ldappasswd -w testrootpassword -s userpassword -xD cn=Manager,dc=example,dc=com uid=jsmith,ou=people,dc=example,dc=com && \
    while true; do sleep 6000; done"]
