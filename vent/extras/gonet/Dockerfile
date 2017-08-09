# build stage
FROM golang:alpine AS builder
MAINTAINER Charlie Lewis <clewis@iqt.org>
COPY main.go /app/main.go
WORKDIR /app
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o gonet .

# final stage
FROM scratch
MAINTAINER Charlie Lewis <clewis@iqt.org>
COPY --from=builder /app/gonet /gonet
CMD ["/gonet"]
