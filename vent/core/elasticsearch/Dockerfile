FROM elasticsearch:2-alpine
MAINTAINER Charlie Lewis <clewis@iqt.org>
RUN plugin install mobz/elasticsearch-head
LABEL vent="" \
      vent.name="elasticsearch" \
      vent.groups="core,search"
