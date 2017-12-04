FROM alpine:3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="rmq_es_connector" \
      vent.groups="core" \
      vent.section="cyberreboot:vent:/vent/core/rmq_es_connector:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"


RUN apk add --update \
    python \
    py2-pip \
    && rm -rf /var/cache/apk/*

COPY requirements.txt /vent/requirements.txt
RUN pip install -r /vent/requirements.txt
COPY rmq_es_connector.py /vent/rmq_es_connector.py

ENTRYPOINT ["python", "/vent/rmq_es_connector.py"]
CMD [""]
