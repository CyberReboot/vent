# build stage
FROM golang:alpine AS builder
COPY main.go /go/src/gonet/main.go
WORKDIR /go/src/gonet
RUN go install

# final stage
FROM alpine:3.6
COPY --from=builder /go/bin/gonet /gonet
CMD ["/gonet"]
