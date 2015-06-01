FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>
RUN apt-get update && apt-get install -y arpwatch \
                                         rsyslog
RUN sed 's/"-N -p"/"-Q"/' -i /etc/default/arpwatch

# runs arpwatch as 'arpwatch' user by default
CMD /etc/init.d/rsyslog start; \
    /etc/init.d/arpwatch start; \
    tail -f /var/log/syslog | grep arpwatch
