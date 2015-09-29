FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y wget
RUN wget http://download.opensuse.org/repositories/network:bro/xUbuntu_14.04/Release.key
RUN apt-key add - < Release.key
RUN sh -c "echo 'deb http://download.opensuse.org/repositories/network:/bro/xUbuntu_14.04/ /' >> /etc/apt/sources.list.d/bro.list"
RUN apt-get update && apt-get install -y bro

WORKDIR /tmp

ENTRYPOINT ["/opt/bro/bin/bro"]
CMD ["-h"]
