FROM alpine:3.6
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    python \
    py2-pip \
    && rm -rf /var/cache/apk/*

COPY . /file-drop
RUN pip install -r /file-drop/requirements.txt

WORKDIR /file-drop

LABEL vent="" \
      vent.name="file-drop" \
      vent.groups="core,files" \
      vent.section="[cyberreboot:vent:/vent/core/file_drop:master:HEAD]"

ENTRYPOINT ["python", "/file-drop/file_drop.py"]

# volume dir to watch
# cmd specify dir
# CMD ["/data"]
