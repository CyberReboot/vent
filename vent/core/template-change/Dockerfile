FROM alpine:3.4
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    python \
    py-pip \
    && rm -rf /var/cache/apk/*

ADD . /template-change
RUN pip install -r /template-change/requirements.txt

WORKDIR /template-change

ENTRYPOINT ["python", "/template-change/template_change.py"]

# volume dir to watch
# cmd specify dir
# CMD ["/data"]
