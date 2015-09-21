import os
import pika
import subprocess
import sys

def connections():
    try:
        path = sys.argv[1]
    except:
        print "no path provided, quitting."
        sys.exit()

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='rabbitmq'))
        channel = connection.channel()

        channel.exchange_declare(exchange='topic_recs',
                                 type='topic')
    except:
        print "unable to connect to rabbitmq, quitting."
        sys.exit()
    return path, channel, connection

def run_tool(path, channel):
    routing_key = "pcap"+sys.argv[1].replace("/", ".")
    output = subprocess.Popen('tshark -r '+path+' -T fields -e frame.time -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport | sort | uniq',
                              shell=True, stdout=subprocess.PIPE)
    text = output.communicate()[0]

    # parse tshark output by tabs and newline
    #
    # expecting:
    # frame_time<tab>src_ip<tab>dst_ip<tab>src_port<tab>dst_port<newline>
    # last line will not have a newline
    #

    recs = text.split("\n")
    for rec in recs:
        data = {}
        fields = rec.split("\t")
        try:
            data["frame_time"] = fields[0]
            data["src_ip"] = fields[1]
            data["dst_ip"] = fields[2]
            data["src_port"] = fields[3]
            data["dst_port"] = fields[4]
            message = str(data)
            channel.basic_publish(exchange='topic_recs',
                                  routing_key=routing_key,
                                  body=message)
            print " [x] Sent %r:%r" % (routing_key, message)
        except:
            pass


if __name__ == '__main__':
    path, channel, connection = connections()
    run_tool(path, channel)
    try:
        connection.close()
    except:
        pass
