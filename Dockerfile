## Image to build from xivo repository

FROM debian:latest
MAINTAINER XiVO Team "dev@avencall.com"

ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root

# Add xivo mirror
RUN echo "deb http://mirror.xivo.io/debian/ xivo-five main" >> /etc/apt/sources.list
ADD http://mirror.xivo.io/xivo_current.key /tmp/
RUN apt-key add /tmp/xivo_current.key
RUN rm /tmp/xivo_current.key
RUN apt-get -qq update
RUN apt-get -qq -y install \
    wget \
    apt-utils \
    ssh \
    xivo-dird

# Add script to run services
ADD xivo-dird-service /root/xivo-dird-service
RUN chmod +x /root/xivo-dird-service

CMD /root/xivo-dird-service

## Image to build from sources

FROM debian:latest
MAINTAINER XiVO Team "dev@avencall.com"

ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root

# Add xivo mirror
RUN echo "deb http://mirror.xivo.io/debian/ xivo-five main" >> /etc/apt/sources.list
ADD http://mirror.xivo.io/xivo_current.key /tmp/
RUN apt-key add /tmp/xivo_current.key
RUN rm /tmp/xivo_current.key

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
    xivo-config \
    xivo-lib-python

# Install xivo-dird
RUN git clone "git://github.com/xivo-pbx/xivo-dird"
WORKDIR xivo-dird
RUN git checkout -t origin/async-plugin
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN touch /var/log/xivo-dird.log
RUN chown www-data: /var/log/xivo-dird.log
RUN cp debian/xivo-dird.init /etc/init.d/xivo-dird
RUN mkdir /etc/xivo/xivo-dird
RUN cp -a examples/xivo-dird.conf examples/plugins.d /etc/xivo/xivo-dird

# Configure nginx
RUN cp examples/xivo-dird.nginx /etc/nginx/sites-available/xivo-dird

# Add script to run services
ADD xivo-dird-service /root/xivo-dird-service
RUN chmod +x /root/xivo-dird-service

CMD /root/xivo-dird-service
