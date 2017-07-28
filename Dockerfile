FROM alpine:3.6
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    docker \
    git \
    python \
    py2-pip \
    && rm -rf /var/cache/apk/*

RUN pip install vent==0.4.2

ENTRYPOINT ["vent"]
CMD [""]
