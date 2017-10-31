FROM alpine:3.6
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"

RUN apk add --update \
    docker \
    git \
    libmagic \
    python \
    py2-pip \
    && rm -rf /var/cache/apk/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install git+git://github.com/cyberreboot/vent.git@master
COPY *.py /

LABEL vent="" \
      vent.name="rq_worker" \
      vent.groups="core,files" \
      vent.section="cyberreboot:vent:/vent/core/rq_worker:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

ENTRYPOINT ["rqworker", "-c", "settings"]
