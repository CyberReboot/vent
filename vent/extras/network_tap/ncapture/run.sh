#!/bin/bash

URI="$1"
INTERVAL="$2"
ID="$3"
ITERS="$4"
FILTER="$5"
# TODO: migrate above static args to getopt style.

# check if filter has '' surrounding it
if [[ "$FILTER" =~ ^\'.*\'$ ]]; then
    FILTER=${FILTER:1:${#FILTER}-2}
fi

# See https://github.com/wanduow/libwdcap for full flag documentation.
# Set CryptoPAn IP anonymization (https://en.wikipedia.org/wiki/Crypto-PAn) with -a (default none).
ANON="none"
# Set checksum updating for anonymization.
CSUM="check"
# Set number of app payload size to keep in bytes.
PAYS="4"
# Set number of DNS payload size to keep in bytes
DPAYS="12"

OUT_PATH="/files/"

while getopts "a:c:d:s:" arg; do
  case $arg in
    a)
      ANON=$OPTARG
      ;;
    c)
      CSUM=$OPTARG
      ;;
    d)
      DPAYS=$OPTARG
      ;;
    o)
      OUT_PATH=$OPTARG
      ;;
    s)
      PAYS=$OPTARG
      ;;
  esac
done

CAPTMP=$(mktemp -d)

make_pcap_name() {
    local id=$1
    local dt=$(date '+%Y-%m-%d_%H_%M_%S')
    echo trace_${id}_${dt}.pcap
}

run_tracecapd() {
    local uri=$1
    local name=$2
    local interval=$3
    local filter=$4

    local dwconf=${CAPTMP}/dw.yaml
    local ppconf=${CAPTMP}/pp.yaml

    # default to interface URI if no prefix.
    # See https://wand.net.nz/trac/libtrace/wiki/SupportedTraceFormats.
    if [[ ! "$uri" =~ .+":".+ ]]; then
        uri="int:$uri"
    fi

    echo -e "format: pcapfile\nnamingscheme: ${name}\ncompressmethod: none\nrotationperiod: day\n" > $dwconf
    echo -e "anon: $ANON\nchecksum: $CSUM\npayload: $PAYS\ndnspayload: $DPAYS\n" > $ppconf
    $(timeout -k2 ${interval}s tracecapd -t 1 -c $dwconf -p $ppconf -s $uri -f "$filter")
}

run_capture() {
    local uri=$1
    local id=$2
    local interval=$3
    local filter=$4
    local out_path=$5

    local name=$(make_pcap_name $id)
    run_tracecapd $uri $name $interval "$filter"
    mv $name $out_path;
    python3 send_message.py $out_path/$name;
}

# if ITERS is non-negative then do the capture ITERS times
if [ $ITERS -gt "0" ]; then
    COUNTER=0
    while [ $COUNTER -lt $ITERS ]; do
        run_capture $URI $ID $INTERVAL "$FILTER" $OUT_PATH
        let COUNTER=COUNTER+1;
    done
else  # else do the capture until killed
    while true
    do
        run_capture $URI $ID $INTERVAL "$FILTER" $OUT_PATH
    done
fi
