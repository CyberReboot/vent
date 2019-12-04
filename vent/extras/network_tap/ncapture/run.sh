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

CAPTMP=$(mktemp -d)

make_pcap_name() {
    local id=$1
    local dt=$(date '+%Y-%m-%d_%H_%M_%S')
    echo trace_${id}_${dt}.pcap
}

run_tracecapd() {
    local nic=$1
    local name=$2
    local interval=$3
    local filter=$4

    local dwconf=${CAPTMP}/dw.yaml
    local ppconf=${CAPTMP}/pp.yaml

    # See https://github.com/wanduow/libwdcap for processing options.
    echo -e "format: pcapfile\nnamingscheme: ${name}\ncompressmethod: none\nrotationperiod: day\n" > $dwconf
    echo -e "anon: none\nchecksum: none\npayload: 4\ndnspayload: 12\n" > $ppconf
    $(timeout -k2 ${interval}s tracecapd -t 1 -c $dwconf -p $ppconf -s int:$nic -f "$filter")
}

run_capture() {
    local nic=$1
    local id=$2
    local interval=$3
    local filter=$4

    local name=$(make_pcap_name $id)
    run_tracecapd $nic $name $interval "$filter"
    mv $name /files/;
    python3 send_message.py $name;
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
