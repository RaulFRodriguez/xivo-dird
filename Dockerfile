FROM debian:latest

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -qq update
RUN apt-get -qq -y install wget apt-utils

# Add xivo mirror
RUN echo "deb http://mirror.xivo.io/debian/ xivo-five main" >> /etc/apt/sources.list
RUN wget http://mirror.xivo.io/xivo_current.key -O - | apt-key add -
RUN apt-get -qq update
RUN apt-get -qq -y install xivo-config xivo-lib-python

# install xivo-dird
RUN apt-get -qq -y install python-pip git libpq-dev python-dev libsasl2-dev libldap2-dev nginx
RUN git clone "git://github.com/xivo-pbx/xivo-dird"
PWD xivo-dird
RUN git checkout -t origin/async-plugin
RUN pip install -r requirements.txt
RUN python setup.py install

# configure environment
RUN adduser  --system --group --quiet --home /var/www --no-create-home --disabled-login www-data
RUN touch /var/log/xivo-dird.log
RUN chown www-data: /var/log/xivo-dird.log
RUN cp debian/xivo-dird.init /etc/init.d/xivo-dird
RUN mkdir /etc/xivo/xivo-dird
RUN cd examples
RUN cp -a xivo-dird.conf plugins.d /etc/xivo/xivo-dird

# configure nginx
RUN cp examples/xivo-dird.nginx /etc/nginx/sites-available
RUN ln -s /etc/nginx/sites-enabled/xivo-dird ../sites-available/xivo-dird
RUN service nginx reload

CMD xivo-dird -f -u www-data
