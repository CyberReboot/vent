# tshark

using python to execute `tshark` commands and then feed into `rabbitmq`.

- note current implementation ends up doing 2 passes of the pcap it is given, which is not optimal.
 - the first pass gets the src/dest with ports and sorts and uniques them.
 - the second pass gets the last packet timestamp so that the records can have a time range.
