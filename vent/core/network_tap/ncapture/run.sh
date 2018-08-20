#!/bin/bash

NIC="$1"
INTERVAL="$2"
ID="$3"
ITERS="$4"
FILTER="$5"

# if ITERS is non-negative then do the capture ITERS times
if [ $ITERS -gt "0" ]; then
    COUNTER=0
    while [ $COUNTER -lt $ITERS ]; do
        dt=$(date '+%Y-%m-%d_%H_%M_%S')
        tcpdump -ni $NIC --no-tcpudp-payload -w 'trace_'"$ID"'_'"$dt"'.pcap' $FILTER &
        pid=$!
        sleep $INTERVAL
        kill $pid
        mv *.pcap /files/;
        let COUNTER=COUNTER+1;
    done
else  # else do the capture until killed
    while true
    do
        dt=$(date '+%Y-%m-%d_%H_%M_%S')
        tcpdump -ni $NIC --no-tcpudp-payload -w 'trace_'"$ID"'_'"$dt"'.pcap' $FILTER &
        pid=$!
        sleep $INTERVAL
        kill $pid
        mv *.pcap /files/;
    done
fi
