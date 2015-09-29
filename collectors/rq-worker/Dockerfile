FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y python-pip
RUN pip install rq
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD settings.py settings.py
ADD pcap_drop.py pcap_drop.py

ENTRYPOINT ["rqworker", "-c", "settings"]
