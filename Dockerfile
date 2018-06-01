FROM alpine:3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"

RUN apk add --update \
    docker \
    git \
    python3 \
    py3-pip \
    && rm -rf /var/cache/apk/*

RUN pip3 install git+git://github.com/cyberreboot/vent.git@master

RUN mkdir /root/.vent
VOLUME ["/root/.vent"]

ENV VENT_CONTAINERIZED true

ENTRYPOINT ["vent"]
CMD [""]
