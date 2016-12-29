FROM alpine:3.5
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    docker \
    libmagic \
    python \
    py2-pip \
    && rm -rf /var/cache/apk/*

RUN pip install rq
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD *.py /

ENTRYPOINT ["rqworker", "-c", "settings"]
