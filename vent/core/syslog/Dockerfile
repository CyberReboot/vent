FROM debian:stretch-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="syslog" \
      vent.groups="core,logging,syslog" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"


RUN apt-get update -qq && apt-get install -y syslog-ng telnet && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
EXPOSE 514

HEALTHCHECK --interval=15s --timeout=15s \
 CMD logger -p cron.info "Testing health of syslog"

ENTRYPOINT ["/usr/sbin/syslog-ng", "-F", "-f", "/etc/syslog-ng/syslog-ng.conf"]
