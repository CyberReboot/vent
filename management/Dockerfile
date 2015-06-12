FROM alpine
MAINTAINER Charlie Lewis <clewis@iqt.org>
RUN apk add --update curl jq netcat-openbsd && rm -rf /var/cache/apk/*
ADD run_tools.sh /run_tools.sh
CMD ["/run_tools.sh"]
