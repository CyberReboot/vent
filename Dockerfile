FROM alpine:3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"

RUN apk add --update \
    curl \
    docker \
    git \
    python3 \
    py3-pip \
    && rm -rf /var/cache/apk/*

RUN pip3 install --upgrade pip

# healthcheck
COPY healthcheck /healthcheck
RUN pip3 install -r /healthcheck/requirements.txt
ENV FLASK_APP /healthcheck/hc.py
HEALTHCHECK --interval=15s --timeout=15s CMD curl --silent --fail http://localhost:5000/healthcheck || exit 1

COPY . /vent
RUN pip3 install /vent

RUN mkdir /root/.vent
VOLUME ["/root/.vent"]

ENV VENT_CONTAINERIZED true

CMD  (flask run > /dev/null 2>&1) & (vent)
