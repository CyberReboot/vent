FROM alpine
MAINTAINER Charlie Lewis <clewis@iqt.org>
RUN apk add --update bash git jq netcat-openbsd && rm -rf /var/cache/apk/*
ADD execute.sh /execute.sh
CMD ["/execute.sh", "/dns-data/dyn_data/output.csv"]
