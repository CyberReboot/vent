FROM alpine:3.6
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    syslog-ng \
    && rm -rf /var/cache/apk/*

COPY syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
EXPOSE 514

LABEL vent="" \
      vent.name="syslog" \
      vent.groups="core,logging,syslog" \
      vent.section="cyberreboot:vent:/vent/core/rq_worker:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

ENTRYPOINT ["/usr/sbin/syslog-ng", "-F", "-f", "/etc/syslog-ng/syslog-ng.conf"]
