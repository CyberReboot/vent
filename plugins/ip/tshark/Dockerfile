FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y python-pip tshark

ADD tshark_ip_to_rabbit.py tshark_ip_to_rabbit.py
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "tshark_ip_to_rabbit.py"]
CMD [""]
