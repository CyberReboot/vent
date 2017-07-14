FROM alpine:3.6
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    bash \
    tcpdump \
    && rm -rf /var/cache/apk/*

VOLUME /tmp
WORKDIR /tmp
COPY run.sh run.sh

LABEL vent="" \
      vent.name="file-drop" \
      vent.groups="collection,network"

CMD /tmp/run.sh
