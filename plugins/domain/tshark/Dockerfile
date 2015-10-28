FROM alpine:3.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    bash \
    python \
    py-pip \
    tshark \
    && rm -rf /var/cache/apk/*

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD tshark_domain_to_rabbit.py tshark_domain_to_rabbit.py
ADD tshark.sh tshark.sh

ENTRYPOINT ["python", "tshark_domain_to_rabbit.py"]
CMD [""]
