FROM alpine:3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="syslog" \
      vent.groups="core,logging,syslog" \
      vent.section="cyberreboot:vent:/vent/core/syslog:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"


RUN apk add --update \
    syslog-ng \
    && rm -rf /var/cache/apk/*

COPY syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
EXPOSE 514

ENTRYPOINT ["/usr/sbin/syslog-ng", "-F", "-f", "/etc/syslog-ng/syslog-ng.conf"]
