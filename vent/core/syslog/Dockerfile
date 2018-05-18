FROM debian:stretch-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="syslog" \
      vent.groups="core,logging,syslog" \
      vent.section="cyberreboot:vent:/vent/core/syslog:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"


RUN apt-get update -qq && apt-get install -y syslog-ng

COPY syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
EXPOSE 514

ENTRYPOINT ["/usr/sbin/syslog-ng", "-F", "-f", "/etc/syslog-ng/syslog-ng.conf"]
