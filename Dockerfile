FROM ubuntu:14.04
MAINTAINER matthew@dockstudios.co.uk
RUN apt-get -qq update && apt-get -yqq upgrade && apt-get -yqq install python2.7 python-pip python-ldap python-jinja2 python-psycopg2 python-redis python-enum34 python-pil python-dev
RUN pip install django==1.8.7 dj-database-url SkPy celery
RUN pip install requests redis --upgrade
RUN mkdir /code
WORKDIR /code
ADD . /code/

EXPOSE 5000
ENTRYPOINT ["./start.sh"]
