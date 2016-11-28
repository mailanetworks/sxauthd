FROM centos:6
RUN echo 'deltarpm=0' >> /etc/yum.conf && \
    sed -i 's/^mirrorlist=/#mirrorlist=/' /etc/yum.repos.d/* && \
    sed -i 's/^#baseurl=/baseurl=/' /etc/yum.repos.d/* && \
    sed -i 's/enabled=1/enabled=0/' /etc/yum/pluginconf.d/fastestmirror.conf && \
    yum install -y epel-release && yum clean all
RUN yum install -y python python-pip python-setuptools python-virtualenv git && \
    yum clean all
COPY buildpy26.sh /root/
RUN virtualenv venv/ && \
    . venv/bin/activate && \
    pip install setuptools-git
CMD ["/bin/bash","/root/buildpy26.sh"]
