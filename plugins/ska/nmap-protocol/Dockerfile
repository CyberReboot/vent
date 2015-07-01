FROM alpine
MAINTAINER Charlie Lewis <clewis@iqt.org>
RUN apk add --update bash jq netcat-openbsd && rm -rf /var/cache/apk/*
ADD execute.sh /execute.sh
ADD output.csv /output.csv
CMD ["/execute.sh"]
