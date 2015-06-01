FROM python:2.7.9
MAINTAINER Charlie Lewis <clewis@iqt.org>

ADD . /scan
WORKDIR /scan

CMD hostname --all-ip-addresses | \
    awk '{for(i=1;i<=NF;i++){printf "%s\n", $i};}' | \
    awk -F'.' '{printf "./ping-map.py %s.%s.%s.x\n", $1,$2,$3}' >> runner.sh && \
    sleep 1 && \
    ./runner.sh
