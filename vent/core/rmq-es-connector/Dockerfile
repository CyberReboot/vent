FROM alpine:3.5
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    python \
    py2-pip \
    && rm -rf /var/cache/apk/*

ADD requirements.txt /vent/requirements.txt
RUN pip install -r /vent/requirements.txt
ADD rmq_es_connector.py /vent/rmq_es_connector.py

LABEL vent="" \
      vent.name="rmq-es-connector" \
      vent.groups="core"

ENTRYPOINT ["python", "/vent/rmq_es_connector.py"]
CMD [""]
