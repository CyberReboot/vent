FROM alpine:3.3
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    python \
    py-pip \
    && rm -rf /var/cache/apk/*

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD rmq_es_connector.py rmq_es_connector.py

ENTRYPOINT ["python", "rmq_es_connector.py"]
CMD [""]
