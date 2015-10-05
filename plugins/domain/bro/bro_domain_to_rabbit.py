import os
import pika
import subprocess
import sys
import time

def get_path():
    try:
        path = sys.argv[1]
    except:
        print "no path provided, quitting."
        sys.exit()
    return path

def connections():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='rabbitmq'))
        channel = connection.channel()

        channel.exchange_declare(exchange='topic_recs',
                                 type='topic')
    except:
        print "unable to connect to rabbitmq, quitting."
        sys.exit()
    return channel, connection

def run_tool(path):
    routing_key = "domain"+sys.argv[1].replace("/", ".")

    subprocess.Popen('/opt/bro/bin/bro -r '+path, shell=True, stdout=subprocess.PIPE).wait()
    subprocess.Popen('/bin/bash bro.sh dns.log', shell=True, stdout=subprocess.PIPE).wait()

    start_time = 0
    get_start_time = subprocess.Popen("/bin/sed '9q;d' dns.log | /usr/bin/awk '{print $1}'",
                              shell=True, stdout=subprocess.PIPE)
    start_time = get_start_time.communicate()[0]

    end_time = 0
    get_end_time = subprocess.Popen("/usr/bin/tail -n2 dns.log | /usr/bin/head -n1 | /usr/bin/awk '{print $1}'",
                              shell=True, stdout=subprocess.PIPE)
    end_time = get_end_time.communicate()[0]

    # parse bro output by commas and newline
    #
    # expecting:
    # query_count<space>ip<comma>domain<newline>
    # last line will not have a newline
    #

    channel, connection = connections()
    print "sending pcap results..."
    with open('/tmp/results.out', 'r') as f:
        for rec in f:
            data = {}
            rec = rec.lstrip()
            count = rec.split(" ", 1)
            fields = count[1].split(",")
            try:
                data["query_count"] = count[0].strip()
                # these are in epoch, probably should be converted
                data["frame_begin_range"] = start_time.strip()
                data["frame_end_range"] = end_time.strip()
                data["ip"] = fields[0].strip()
                data["domain"] = fields[1].strip()
                data["tool"] = "bro"
                message = str(data)
                channel.basic_publish(exchange='topic_recs',
                                      routing_key=routing_key,
                                      body=message)
                print " [x] Sent %r:%r" % (routing_key, message)
            except:
                pass
    try:
        connection.close()
    except:
        pass

if __name__ == '__main__':
    path = get_path()
    run_tool(path)
