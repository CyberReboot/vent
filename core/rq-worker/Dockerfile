FROM alpine:3.3
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    python \
    py-pip \
    && rm -rf /var/cache/apk/*

RUN pip install rq
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD settings.py settings.py
ADD pcap_drop.py pcap_drop.py

ENTRYPOINT ["rqworker", "-c", "settings"]
