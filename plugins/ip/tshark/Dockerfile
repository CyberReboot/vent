FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y tshark
ENTRYPOINT ["tshark"]
CMD ["-h"]
