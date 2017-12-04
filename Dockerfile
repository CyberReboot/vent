FROM alpine:3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"

RUN apk add --update \
    docker \
    git \
    python \
    py2-pip \
    && rm -rf /var/cache/apk/*

RUN pip install git+git://github.com/cyberreboot/vent.git@master

RUN mkdir /root/.vent
VOLUME ["/root/.vent"]

ENV VENT_CONTAINERIZED true

ENTRYPOINT ["vent"]
CMD [""]
