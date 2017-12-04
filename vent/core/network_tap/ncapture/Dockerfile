FROM alpine:3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="file-drop" \
      vent.groups="collection,hidden,network,network_tap_child"

RUN apk add --update \
    bash \
    tcpdump \
    && rm -rf /var/cache/apk/*

VOLUME /tmp
WORKDIR /tmp
COPY run.sh run.sh

CMD /tmp/run.sh
