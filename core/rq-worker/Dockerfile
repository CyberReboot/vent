FROM alpine:3.4
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    docker \
    python \
    py-pip \
    && rm -rf /var/cache/apk/*

RUN pip install rq
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD *.py /

ENTRYPOINT ["rqworker", "-c", "settings"]
