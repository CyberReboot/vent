FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y build-essential \
                                         python-dev \
                                         python-setuptools \
                                         python-software-properties \
                                         software-properties-common

ADD . /scan
WORKDIR /scan

CMD hostname --all-ip-addresses | \
    awk '{for(i=1;i<=NF;i++){printf "%s\n", $i};}' | \
    awk -F'.' '{printf "./ping-map.py %s.%s.%s.x\n", $1,$2,$3}' >> runner.sh && \
    sleep 1 && \
    ./runner.sh
