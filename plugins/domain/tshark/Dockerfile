FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y python-pip tshark

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD tshark_domain_to_rabbit.py tshark_domain_to_rabbit.py
ADD tshark.sh tshark.sh

ENTRYPOINT ["python", "tshark_domain_to_rabbit.py"]
CMD [""]
