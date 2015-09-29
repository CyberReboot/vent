FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y python-pip
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD rmq_es_connector.py rmq_es_connector.py

ENTRYPOINT ["python", "rmq_es_connector.py"]
CMD [""]
