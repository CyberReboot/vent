FROM alpine:3.6
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    docker \
    gcc \
    git \
    libmagic \
    linux-headers \
    musl-dev \
    python \
    python-dev \
    py2-pip \
    && rm -rf /var/cache/apk/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install git+git://github.com/cyberreboot/vent.git@master
COPY *.py /

LABEL vent="" \
      vent.name="rq-worker" \
      vent.groups="core,files"

ENTRYPOINT ["rqworker", "-c", "settings"]
