FROM alpine:3.6
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    docker \
    git \
    python \
    py2-pip \
    && rm -rf /var/cache/apk/*

ENV REFRESHED_AT 090720171433
RUN pip install git+git://github.com/cglewis/vent.git@master

ENTRYPOINT ["vent"]
CMD [""]
