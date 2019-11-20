#!/bin/bash

NIC="$1"
INTERVAL="$2"
ID="$3"
ITERS="$4"
FILTER="$5"

# check if filter has '' surrounding it
if [[ $FILTER =~ ^\'.*\'$ ]]; then
    FILTER=${FILTER:1:${#FILTER}-2}
fi

make_pcap_name() {
    local id=$1
    local dt=$(date '+%Y-%m-%d_%H_%M_%S')
    echo trace_${id}_${dt}.pcap
}

# if ITERS is non-negative then do the capture ITERS times
if [ $ITERS -gt "0" ]; then
    COUNTER=0
    while [ $COUNTER -lt $ITERS ]; do
	name=$(make_pcap_name $ID)
        tcpdump -ni $NIC --no-tcpudp-payload -w $name $FILTER &
        pid=$!
        sleep $INTERVAL
        kill $pid
        mv *.pcap /files/;
        let COUNTER=COUNTER+1;
    done
else  # else do the capture until killed
    while true
    do
	name=$(make_pcap_name $ID)
        tcpdump -ni $NIC --no-tcpudp-payload -w $name $FILTER &
        pid=$!
        sleep $INTERVAL
        kill $pid
        mv *.pcap /files/;
    done
fi
