# build stage
FROM golang:alpine AS builder
MAINTAINER Charlie Lewis <clewis@iqt.org>
COPY main.go /go/src/gonet/main.go
WORKDIR /go/src/gonet
RUN go install

# final stage
FROM alpine:3.6
MAINTAINER Charlie Lewis <clewis@iqt.org>
COPY --from=builder /go/bin/gonet /gonet
CMD ["/gonet"]
