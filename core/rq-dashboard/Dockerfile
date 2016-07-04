FROM alpine:3.4
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    git \
    python \
    py-pip \
    && rm -rf /var/cache/apk/*

# get newer for worker list fix
RUN pip install git+https://github.com/mredar/rq-dashboard.git

ADD rq_dash_settings.py /rq_dash_settings.py

ADD run.sh /run.sh
RUN chmod 755 /run.sh

EXPOSE 9181

CMD ["/run.sh"]
