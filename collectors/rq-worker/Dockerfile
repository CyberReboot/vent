FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y python-pip
RUN pip install rq
ADD settings.py settings.py

ENTRYPOINT ["rqworker", "-c", "settings"]
