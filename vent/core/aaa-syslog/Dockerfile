FROM alpine:3.5
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    syslog-ng \
    && rm -rf /var/cache/apk/*

ADD syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
EXPOSE 514

ENTRYPOINT ["/usr/sbin/syslog-ng", "-F", "-f", "/etc/syslog-ng/syslog-ng.conf"]
