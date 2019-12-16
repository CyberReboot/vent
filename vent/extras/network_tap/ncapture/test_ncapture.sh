#!/bin/bash

# smoke test for ncapture worker
# requires tcpdump and tshark to be installed.

URI=lo
IP=127.0.0.1
SIZE=1000
MAXCAPLEN=50

TMPDIR=$(mktemp -d)

docker build -f Dockerfile . -t cyberreboot/vent-ncapture
echo starting ncapture
docker run --privileged --net=host --cap-add=NET_ADMIN -v $TMPDIR:/files -t cyberreboot/vent-ncapture /tmp/run.sh $URI 15 test 1 "host $IP and icmp" -d 12 -s 4 -a none -c none -o /files/ || exit 1 &
echo waiting for pcap
while [ "$(find $TMPDIR -prune -empty)" ] ; do
  ping -q -n -i 0.1 -s $SIZE -c 10 $IP > /dev/null
  echo -n .
done
tcpdump -n -r $TMPDIR/*pcap greater $SIZE > $TMPDIR/greater.txt || exit 1
if [ ! -s $TMPDIR/greater.txt ] ; then
  echo "FAIL: no packets with original size $SIZE"
  exit 1
fi
CAPLEN=$(capinfos -l $TMPDIR/*cap|grep -E 'Packet size limit:\s+inferred: [0-9]+ bytes'|grep -o -E '[0-9]+')
if [ "$CAPLEN" == "" ] ; then
  echo "FAIL: capture length not limited"
  exit 1
fi
if [ "$CAPLEN" -gt $MAXCAPLEN ] ; then
  echo "FAIL: capture length $CAPLEN over limit (payload not stripped?)"
  exit 1
fi
echo ok

rm -rf $TMPDIR
