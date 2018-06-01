FROM alpine:3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="file_drop" \
      vent.groups="core,files" \
      vent.section="cyberreboot:vent:/vent/core/file_drop:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

RUN apk add --update \
    python3 \
    py3-pip \
    && rm -rf /var/cache/apk/*

COPY . /file-drop
RUN pip3 install -r /file-drop/requirements.txt

WORKDIR /file-drop

ENTRYPOINT ["python3", "/file-drop/file_drop.py"]

# volume dir to watch
# cmd specify dir
# CMD ["/data"]
