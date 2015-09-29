FROM debian:wheezy
MAINTAINER Mark Redar mredar@gmail.com

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get clean

RUN apt-get install -y -q python
RUN apt-get install -y -q python-pip
RUN apt-get install -y -q git

#get newer for worker list fix
RUN pip install git+https://github.com/mredar/rq-dashboard.git

ADD rq-dash-settings.py /rq-dash-settings.py

ADD run.sh /run.sh
RUN chmod 755 /run.sh

EXPOSE 9181

CMD ["/run.sh"]
