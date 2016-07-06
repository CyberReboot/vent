def pcap_queue(path):
    """
    Processes PCAP files that have been added from the rq-worker, and tells
    vent-management to start plugins for the new file.
    """
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
        plugin_array = []
        # Check section exists and has options
        if config.has_section("plugins") and config.options("plugins"):
            plugin_array = config.options("plugins")
        plugins = {}
        for plug in plugin_array:
            if plug not in ["core", "visualization", "collectors"]:
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

def template_queue(path):
    """
    Processes template files that have been added or changed or deleted from
    the rq-worker, and tells vent-management to restart containers based on
    changes made to the templates.
    """
    import os
    import sys
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

    # check for template type
    try:
        template = path.split("/")[-1]
        if template == "modes.template":
            # !! TODO
            pass
        elif template == "core.template":
            # check if the container is this one and kill it last!
            hostname = os.environ.get('HOSTNAME')
            current_container = hostname
            core_containers = c.containers(all=True, filters={'name':"core"})
            for cont in core_containers:
                if cont['Id'].startswith(current_container):
                    current_container = cont['Id']
                else:
                    try:
                        c.kill(cont['Id'])
                        c.remove_container(cont['Id'])
                    except Exception as e:
                        pass
            if len(core_containers) > 0:
                os.system('python2.7 /vent/template_parser.py core start')
            # !! TODO failing, so commenting out for now
            #c.restart(current_container)
        elif template == "collectors.template":
            active_containers = c.containers(quiet=True, all=True, filters={'name':"active"})
            for cont in active_containers:
                try:
                    c.kill(cont['Id'])
                    c.remove_container(cont['Id'])
                except Exception as e:
                    pass
            if len(active_containers) > 0:
                os.system('python2.7 /vent/template_parser.py active start')
            passive_containers = c.containers(quiet=True, all=True, filters={'name':"passive"})
            for cont in passive_containers:
                try:
                    c.kill(cont['Id'])
                    c.remove_container(cont['Id'])
                except Exception as e:
                    pass
            if len(passive_containers) > 0:
                os.system('python2.7 /vent/template_parser.py passive start')
        elif template == "visualization.template":
            viz_containers = c.containers(quiet=True, all=True, filters={'name':"visualization"})
            for cont in viz_containers:
                try:
                    c.kill(cont['Id'])
                    c.remove_container(cont['Id'])
                except Exception as e:
                    pass
            if len(viz_containers) > 0:
                os.system('python2.7 /vent/template_parser.py visualization start')
        else:
            pass
            # plugin
    except Exception as e:
        pass
    return
