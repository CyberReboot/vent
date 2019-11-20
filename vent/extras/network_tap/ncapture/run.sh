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

run_tcpdump() {
    local nic=$1
    local filter=$2
    echo tcpdump -ni $nic --no-tcpudp-payload -w $name $filter
    $(tcpdump -ni $nic $name $filter) &
}

run_capture() {
    local nic=$1
    local id=$2
    local interval=$3
    local filter=$4

    echo sleep: $interval

    local name=$(make_pcap_name $id)
    run_tcpdump $nic $filter
    pid=$!
    kill $pid
    mv *.pcap /files/;
}

# if ITERS is non-negative then do the capture ITERS times
if [ $ITERS -gt "0" ]; then
    COUNTER=0
    while [ $COUNTER -lt $ITERS ]; do
	run_capture $NIC $ID $INTERVAL "$FILTER"
        let COUNTER=COUNTER+1;
    done
else  # else do the capture until killed
    while true
    do
        run_capture $NIC $ID $INTERVAL "$FILTER"
    done
fi
