#!/bin/bash
TYPE="$1"
PATH="$2"
/usr/bin/tshark -r $PATH -T fields -e ip.$TYPE -e eth.$TYPE | /usr/bin/tee >(/usr/bin/sort | /usr/bin/uniq -c > /tmp/results_$TYPE.out) >(/usr/bin/wc -l > /tmp/count.out) > /dev/null
