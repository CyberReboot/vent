#!/usr/bin/env python
import os
import sys
import time
from multiprocessing import Pool
from subprocess import Popen, PIPE

# ignore ipv6 for now...since icmp is blocked by default
# read in network range
# read in dns list from host -l DOMAIN
# try both dns name and ip address

network = "x.x.x.x"

def check_host(x):
    global network
    subnet = network.split(".")
    host = ".".join(subnet[0:3])+"."+str(x)
    response = os.system("ping -W1 -c 1 " + host + "> /dev/null")

    rows,columns = os.popen('stty size', 'r').read().split()
    rows = int(rows)
    columns = int(columns)

    sys.stdout.write('\r')
    sys.stdout.write(' ' * columns)
    sys.stdout.write('\r')

    #and then check the response...
    if response == 0:
        sys.stdout.write('{} is up!'.format(host))
    else:
        sys.stdout.write('{} is down!'.format(host))
    sys.stdout.flush()
    return response

start_time = time.time()

if len(sys.argv) < 2:
    print "please supply a network subnet"
    print "example: \"10.10.10.x\" rather than 10.10.10.0/24"
    sys.exit()

domains = None
if len(sys.argv) == 3:
    domains = sys.argv[2]
    domains = domains.split(" ")

if domains:
    for domain in domains:
        unmatched = {}
        hostnames_up = []
        hostnames_down = []
        ips_up = []
        ips_down = []
        ipv6_hosts = {}
        name_servers = []
        total_up = 0
        total_down = 0
        total = 0
        p = Popen(['host', '-l', domain], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        response = p.stdout.read()
        if "Transfer failed" in response:
            print response
        else:
            lines = response.split("\n")
            for line in lines[:-1]:
                parts = line.split(" has address ")
                if len(parts) == 2:
                    response = os.system("ping -W1 -c 1 " + parts[0] + "> /dev/null")
                    up1 = 1
                    up2 = 1
                    if response == 0:
                        hostnames_up.append(parts[0])
                    else:
                        hostnames_down.append(parts[0])
                        up1 = 0
                    response = os.system("ping -W1 -c 1 " + parts[1] + "> /dev/null")
                    if response == 0:
                        ips_up.append(parts[1])
                    else:
                        ips_down.append(parts[1])
                        up2 = 0
                    if up1+up2 == 1:
                        unmatched[parts[0]+":"+str(up1)] = parts[1]+":"+str(up2)
                        total_up += 1
                    elif up1+up2 == 2:
                        total_up += 1
                    else:
                        total_down += 1
                    total += 1
                else:
                    parts = line.split(" has IPv6 address ")
                    if len(parts) == 2:
                        response = os.system("ping -W1 -c 1 " + parts[0] + "> /dev/null")
                        if response == 0:
                            hostnames_up.append(parts[0])
                            total_up += 1
                        else:
                            hostnames_down.append(parts[0])
                            total_down += 1
                        ipv6_hosts[parts[0]] = parts[1]
                        total += 1
                    else:
                        parts = line.split(" name server ")
                        if len(parts) == 2:
                            response = os.system("ping -W1 -c 1 " + parts[1] + "> /dev/null")
                            if response == 0:
                                hostnames_up.append(parts[1])
                                total_up += 1
                            else:
                                hostnames_down.append(parts[1])
                                total_down += 1
                            name_servers.append(parts[1])
                            total += 1
                        else:
                            print "unknown record:", line
        print
        print "unmatched:", len(unmatched)
        print unmatched
        print
        print "hostnames up:", len(hostnames_up)
        print hostnames_up
        print
        print "hostnames down:", len(hostnames_down)
        print hostnames_down
        print
        print "ips up:", len(ips_up)
        print ips_up
        print
        print "ips down:", len(ips_down)
        print ips_down
        print
        print "ipv6 hosts:", len(ipv6_hosts)
        print ipv6_hosts
        print
        print "name servers:", len(name_servers)
        print name_servers
        print
        print "total up:", total_up
        print "total down:", total_down
        print "total:", total
        print

# error checking
try:
    subnet = sys.argv[1].split(".")
except:
    print "invalid network subnet"
    sys.exit()
if len(subnet) != 4:
    print "invalid network subnet"
    sys.exit()
for num in subnet:
    try:
        if num != 'x' and (int(num) < 0 or int(num) > 256):
            print "invalid network subnet"
            sys.exit()
    except:
        print "invalid network subnet"
        sys.exit()

networks = {}

# note, simplified version, doesn't allow complex wildcards

# scan all of ipv4 space
if subnet[0] == "x":
    print "you probably don't want to do this"
# scan last three octets only
elif subnet[1] == "x":
    k = 0
    count2 = 0
    while k < 256:
        j = 0
        count3 = 0
        while j < 256:
            network = subnet[0]+"."+str(k)+"."+str(j)+".x"
            pool = Pool(128)
            a = []
            i = 0
            while i < 256:
                a.append(i)
                i += 1
            # if status is 0 the host is alive
            status = pool.map(check_host, a)
            pool.close()
            pool.join()
            count4 = 0
            networks[network] = []
            for idx, code in enumerate(status):
                if code == 0:
                    networks[network].append(idx)
                    count4 += 1
            if count4 == 1:
                print "\n", count4, "host alive on", subnet[0]+"."+str(k)+"."+str(j)+".x\n"
            elif count4 > 1:
                print "\n", count4, "hosts alive on", subnet[0]+"."+str(k)+"."+str(j)+".x\n"
            count3 += count4
            j += 1
        if count3 == 1:
            print "\n", count3, "host alive on", subnet[0]+"."+str(k)+".x.x\n"
        elif count3 > 1:
            print "\n", count3, "hosts alive on", subnet[0]+"."+str(k)+".x.x\n"
        count2 += count3
        k += 1
    if count2 == 1:
        print "\n", count2, "host alive on", ".".join(subnet)
    elif count2 > 1:
        print "\n", count2, "hosts alive on", ".".join(subnet)
# scan last two octets only
elif subnet[2] == "x":
    j = 0
    count3 = 0
    while j < 256:
        network = subnet[0]+"."+subnet[1]+"."+str(j)+".x"
        pool = Pool(128)
        a = []
        i = 0
        while i < 256:
            a.append(i)
            i += 1
        # if status is 0 the host is alive
        status = pool.map(check_host, a)
        pool.close()
        pool.join()
        count4 = 0
        networks[network] = []
        for idx, code in enumerate(status):
            if code == 0:
                networks[network].append(idx)
                count4 += 1
        if count4 == 1:
            print "\n", count4, "host alive on", subnet[0]+"."+subnet[1]+"."+str(j)+".x\n"
        elif count4 > 1:
            print "\n", count4, "hosts alive on", subnet[0]+"."+subnet[1]+"."+str(j)+".x\n"
        count3 += count4
        j += 1
    if count3 == 1:
        print "\n", count3, "host alive on", ".".join(subnet)
    elif count3 > 1:
        print "\n", count3, "hosts alive on", ".".join(subnet)
# scan last octet only, assume at least a /24 needs to be scanned
else:
    network = subnet[0]+"."+subnet[1]+"."+subnet[2]+".x"
    pool = Pool(128)
    a = []
    i = 0
    while i < 256:
        a.append(i)
        i += 1
    # if status is 0 the host is alive
    status = pool.map(check_host, a)
    pool.close()
    pool.join()
    count4 = 0
    networks[network] = []
    for idx, code in enumerate(status):
        if code == 0:
            networks[network].append(idx)
            count4 += 1
    if count4 == 1:
        print "\n", count4, "host alive on", ".".join(subnet)+"\n"
    elif count4 > 1:
        print "\n", count4, "hosts alive on", ".".join(subnet)+"\n"

for network in sorted(networks):
    if len(networks[network]) > 0:
        print network, ":", networks[network]

s = time.time()-start_time
hours, remainder = divmod(s, 3600)
minutes, seconds = divmod(remainder, 60)
print 'time to do scan: %i:%i:%s' % (int(hours), int(minutes), seconds)
