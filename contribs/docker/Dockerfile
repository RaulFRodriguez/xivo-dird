## Image to build from sources

FROM debian:latest
MAINTAINER XiVO Team "dev@avencall.com"

ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root

# Add dependencies
RUN apt-get -qq update
RUN apt-get -qq -y install \
    wget \
    apt-utils \
    python-pip \
    git \
    ssh \
    libpq-dev \
    python-dev \
    libsasl2-dev \
    libldap2-dev \
    nginx \
    curl \
    net-tools

# Install xivo-dird
WORKDIR /root
RUN git clone "git://github.com/xivo-pbx/xivo-dird"
WORKDIR xivo-dird
RUN git checkout -t origin/stevedore-2
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN touch /var/log/xivo-dird.log
RUN chown www-data: /var/log/xivo-dird.log
RUN cp debian/xivo-dird.init /etc/init.d/xivo-dird
RUN mkdir -p /etc/xivo/xivo-dird
RUN mkdir -p  /var/run/xivo-dird
RUN chown www-data: /var/run/xivo-dird
RUN cp -a contribs/examples/xivo-dird.yml contribs/examples/plugins.d /etc/xivo/xivo-dird

# Configure nginx
RUN cp contribs/examples/xivo-dird.nginx /etc/nginx/sites-available/xivo-dird
RUN ln -s /etc/nginx/sites-available/xivo-dird /etc/nginx/sites-enabled/xivo-dird

# Add script to run services
ADD xivo-dird-service /root/xivo-dird-service
RUN chmod +x /root/xivo-dird-service

# Set password
RUN echo "root:xivo" | chpasswd

# Clean
RUN apt-get clean

EXPOSE 50060

CMD /root/xivo-dird-service
