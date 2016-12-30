FROM alpine:3.5
MAINTAINER Charlie Lewis <clewis@iqt.org>
RUN apk add --update bash jq netcat-openbsd && rm -rf /var/cache/apk/*
ADD run_tools.sh /vent/run_tools.sh
CMD ["/vent/run_tools.sh"]
