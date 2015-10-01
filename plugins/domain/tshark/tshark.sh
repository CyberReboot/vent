#!/bin/bash
TYPE="$1"
PATH="$2"
/usr/bin/tshark -r $PATH -T fields -e ip.$TYPE -e dns.qry.name | /usr/bin/tee >(/usr/bin/sort | /usr/bin/uniq -c > /tmp/results_$TYPE.out) >(/usr/bin/wc -l > /tmp/count.out) > /dev/null
