FROM alpine:3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="rmq_es_connector" \
      vent.groups="core" \
      vent.section="cyberreboot:vent:/vent/core/rmq_es_connector:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

RUN apk add --update \
    curl \
    python3 \
    py3-pip \
    && rm -rf /var/cache/apk/*

RUN pip3 install --upgrade pip

# healthcheck
COPY healthcheck /healthcheck
RUN pip3 install -r /healthcheck/requirements.txt
ENV FLASK_APP /healthcheck/hc.py
HEALTHCHECK --interval=15s --timeout=15s \
 CMD curl --silent --fail http://localhost:5000/healthcheck || exit 1

COPY requirements.txt /vent/requirements.txt
RUN pip3 install -r /vent/requirements.txt
COPY rmq_es_connector.py /vent/rmq_es_connector.py

CMD (flask run > /dev/null 2>&1) & (python3 /vent/rmq_es_connector.py)
