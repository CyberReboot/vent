FROM alpine:3.4
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    python \
    py-pip \
    && rm -rf /var/cache/apk/*

ADD . /file-drop
RUN pip install -r /file-drop/requirements.txt

WORKDIR /file-drop

ENTRYPOINT ["python", "/file-drop/file_drop.py"]

# volume dir to watch
# cmd specify dir
# CMD ["/data"]
