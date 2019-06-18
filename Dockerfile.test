FROM elasticsearch:5-alpine
FROM rabbitmq:3-management
FROM redis:alpine
FROM ubuntu:19.04
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"

RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    git \
    make \
    python3 \
    python3-pip \
    software-properties-common

RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
RUN add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable"

RUN apt-get update && apt-get install -y docker-ce
RUN pip3 install --upgrade pip==19.1

RUN echo "https://github.com/cyberreboot/vent:\n  rabbitmq:" >> ~/.vent_startup.yml
ADD . /vent
WORKDIR /vent
RUN pip3 install -r test-requirements.txt
RUN python3 setup.py install

ENTRYPOINT ["pytest"]
CMD ["-l", "-s", "-v", "--cov=.", "--cov-report", "term-missing"]
