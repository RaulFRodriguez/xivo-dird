FROM debian:latest

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -qq update
RUN apt-get -qq -y install apt-utils
RUN apt-get -qq -y install \
     build-essential \
     python \
     python-pip \
     git \
     libpq-dev \
     libldap2-dev \
     libsasl2-dev \
     python-dev

ADD . /root/dird
RUN mkdir -p /var/run/xivo-dird
RUN mkdir -p /etc/xivo-dird/conf.d
RUN chmod a+w /var/run/xivo-dird
RUN touch /var/log/xivo-dird.log
RUN chown www-data: /var/log/xivo-dird.log

WORKDIR /root/dird
RUN cp contribs/docker/listen.yml /etc/xivo-dird/conf.d/
RUN pip install -r requirements.txt
RUN rsync -av etc/ /etc

RUN python setup.py install
RUN rm -fr /root/dird

EXPOSE 9489

CMD xivo-dird -d -f
