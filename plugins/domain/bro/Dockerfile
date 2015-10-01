FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y python-pip wget
RUN wget http://download.opensuse.org/repositories/network:bro/xUbuntu_14.04/Release.key
RUN apt-key add - < Release.key
RUN sh -c "echo 'deb http://download.opensuse.org/repositories/network:/bro/xUbuntu_14.04/ /' >> /etc/apt/sources.list.d/bro.list"
RUN apt-get update && apt-get install -y bro

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD bro_domain_to_rabbit.py bro_domain_to_rabbit.py
ADD bro.sh bro.sh

ENTRYPOINT ["python", "bro_domain_to_rabbit.py"]
CMD [""]
