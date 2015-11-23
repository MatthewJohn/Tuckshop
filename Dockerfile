FROM ubuntu:14.04
MAINTAINER matthew@dockstudios.co.uk
RUN apt-get -qq update && apt-get -yqq upgrade
RUN apt-get -yqq install python2.7 python-pip python-ldap python-jinja2
RUN pip install django dj-database-url
RUN mkdir /code
WORKDIR /code
ADD . /code/

EXPOSE 5000
ENTRYPOINT ["bash", "-c", "python ./manage.py syncdb && python ./tuckshopaccountant.py"]
