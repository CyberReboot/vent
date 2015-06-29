FROM ubuntu:14.04.2
# TODO consider using alpine instead
MAINTAINER Charlie Lewis <clewis@iqt.org>

# should be run with --volumes-from to a container with a volume at /data

RUN apt-get update && apt-get install -y build-essential \
                                         python-dev \
                                         python-setuptools \
                                         python-software-properties \
                                         software-properties-common
RUN easy_install pip
ADD . /collector
RUN pip install -r /collector/requirements.txt

WORKDIR /collector

ENTRYPOINT ["/usr/bin/python", "/collector/collector.py"]

# volume to dir to watch
# # cmd specify dir
# CMD ["/data"]
#
