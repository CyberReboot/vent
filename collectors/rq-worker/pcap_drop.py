def pcap_queue(path):
    from docker import Client
    c = Client(base_url='unix://var/run/docker.sock')
    container = c.create_container(image='ip/tshark', volumes=["/data:/data"], command="-r "+path+" -T fields -e ip.src -e dns.qry.name | sort | uniq > /data/test.out")
    response = c.start(container=container.get('Id'))
    return response
