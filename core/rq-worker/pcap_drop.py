def pcap_queue(path):
    import os
    import time

    import ConfigParser
    config = ConfigParser.RawConfigParser()

    from docker import Client
    from docker.utils.types import LogConfig
    c = Client(base_url='unix://var/run/docker.sock')

    # first some cleanup
    containers = c.containers(quiet=True, all=True, filters={'status':"exited"})
    for cont in containers:
        try:
            # will only remove containers that aren't running
            c.remove_container(cont['Id'])
        except Exception as e:
            pass

    template_dir = "/var/lib/docker/data/templates/"
    plugins_dir = "/var/lib/docker/data/plugins/"
    try:
        config.read(template_dir+'modes.template')
        plugin_array = config.options("plugins")
        plugins = {}
        for plug in plugin_array:
            if plug != "core" and plug != "visualization" and plug != "collectors":
                plugins[plug] = config.get("plugins", plug)

        container_count = 0
        container_max = 50
        try:
            config.read(template_dir+'core.template')
            container_max = int(config.get("active-containers", "count"))
        except Exception as e:
            pass
        for plugin in plugins:
            # check resources before creating container
            # wait until there are resources available
            container_count = len(c.containers(filters={'status':'running'}))
            while container_count >= container_max:
                time.sleep(5)
                container_count = len(c.containers(filters={'status':'running'}))

            cmd = "python2.7 /vent/template_parser.py "+plugin+" start "+path
            os.system(cmd)
    except Exception as e:
        pass
    return
