FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>
RUN apt-get update && apt-get install -y git \
                                         python-dev \
                                         python-setuptools
RUN easy_install pip

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD . /endpoint
WORKDIR /endpoint
EXPOSE 8080

ENTRYPOINT ["/usr/bin/env", "python"]
CMD ["endpoint.py"]

