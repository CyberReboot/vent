FROM alpine:3.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    arpwatch \
    rsyslog \
    && rm -rf /var/cache/apk/*

RUN sed 's/"-N -p"/"-Q"/' -i /etc/conf.d/arpwatch

# runs arpwatch as 'arpwatch' user by default
CMD /etc/init.d/rsyslog start; \
    /etc/init.d/arpwatch start; \
    tail -f /var/log/syslog | grep arpwatch
