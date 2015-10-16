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
    routing_key = "mac"+sys.argv[1].replace("/", ".")
    start_time = 0
    get_start_time = subprocess.Popen('tshark -r '+path+' -c 1 -T fields -e frame.time',
                              shell=True, stdout=subprocess.PIPE)
    start_time = get_start_time.communicate()[0]
    start_time = start_time.split(".")
    start_time = str(time.mktime(time.strptime(start_time[0], "%b %d, %Y %H:%M:%S")))
    subprocess.Popen('/bin/bash tshark.sh src '+path, shell=True, stdout=subprocess.PIPE).wait()
    subprocess.Popen('/bin/bash tshark.sh dst '+path, shell=True, stdout=subprocess.PIPE).wait()

    print "processing frame count..."
    frame_number = -1
    while frame_number == -1:
        try:
            with open('/tmp/count.out', 'r') as f:
                frame_number = f.readline().strip()
        except:
            pass
        time.sleep(1)

    end_time = 0
    get_end_time = subprocess.Popen('tshark -r '+path+' -Y frame.number=='+frame_number+' -T fields -e frame.time',
                                    shell=True, stdout=subprocess.PIPE)
    end_time = get_end_time.communicate()[0]
    end_time = end_time.split(".")
    end_time = str(time.mktime(time.strptime(end_time[0], "%b %d, %Y %H:%M:%S")))

    # parse tshark output by tabs and newline
    #
    # expecting:
    # packet_count<space>ip<tab>eth<newline>
    # last line will not have a newline
    #

    print "processing pcap results..."
    while end_time == 0:
        time.sleep(1)

    channel, connection = connections()
    print "sending pcap results..."
    with open('/tmp/results_src.out', 'r') as f:
        for rec in f:
            data = {}
            rec = rec.lstrip()
            count = rec.split(" ", 1)
            fields = count[1].split("\t")
            try:
                data["packet_count"] = count[0].strip()
                data["frame_begin_range"] = start_time.strip()
                data["frame_end_range"] = end_time.strip()
                data["ip"] = fields[0].strip()
                data["eth"] = fields[1].strip()
                data["tool"] = "tshark"
                message = str(data)
                channel.basic_publish(exchange='topic_recs',
                                      routing_key=routing_key,
                                      body=message)
                print " [x] Sent %r:%r" % (routing_key, message)
            except:
                pass

    with open('/tmp/results_dst.out', 'r') as f:
        for rec in f:
            data = {}
            rec = rec.lstrip()
            count = rec.split(" ", 1)
            fields = count[1].split("\t")
            try:
                data["packet_count"] = count[0].strip()
                data["frame_begin_range"] = start_time.strip()
                data["frame_end_range"] = end_time.strip()
                data["ip"] = fields[0].strip()
                data["eth"] = fields[1].strip()
                data["tool"] = "tshark"
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
