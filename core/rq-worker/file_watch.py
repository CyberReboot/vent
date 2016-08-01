def file_queue(path, base_dir="/var/lib/docker/data/"):
    """
    Processes files that have been added from the rq-worker, and tells
    vent-management to start plugins that match the mime type for the new file.
    """
    import ConfigParser
    import magic
    import os
    import time

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

    template_dir = base_dir+"templates/"
    plugins_dir = base_dir+"plugins/"
    vent_dir = "/data/"
    if base_dir != "/var/lib/docker/data/":
        vent_dir = base_dir
    try:
        config = ConfigParser.RawConfigParser()
        # needed to preserve case sensitive options
        config.optionxform=str
        # Check file exists
        if os.path.isfile(template_dir+'modes.template'):
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
            config = ConfigParser.RawConfigParser()
            # needed to preserve case sensitive options
            config.optionxform=str
            if os.path.isfile(template_dir+'core.template'):
                config.read(template_dir+'core.template')
            if config.has_section("active-containers") and config.has_option("active-containers", "count"):
                container_max = int(config.get("active-containers", "count"))
        except Exception as e:
            print(str(e))

        file_mime = None
        try:
            f_path = path.split("_", 1)[1]
            file_mime = magic.from_file(f_path, mime=True)
        except Exception as e:
            print(str(e))

        for plugin in plugins:
            # check mime types
            mime_types = []
            try:
                config = ConfigParser.RawConfigParser()
                # needed to preserve case sensitive options
                config.optionxform=str
                if os.path.isfile(template_dir+plugin+'.template'):
                    config.read(template_dir+plugin+'.template')
                if config.has_section("service") and config.has_option("service", "mime_types"):
                    mime_types = config.get("service", "mime_types").split(",")
            except Exception as e:
                print(str(e))
            if len(mime_types) == 0 or file_mime in mime_types:
                # check resources before creating container
                # wait until there are resources available
                container_count = len(c.containers(filters={'status':'running'}))
                while container_count >= container_max:
                    time.sleep(5)
                    container_count = len(c.containers(filters={'status':'running'}))
                cmd = "python2.7 "+vent_dir+"template_parser.py "+plugin+" start "+path
                os.system(cmd)
    except Exception as e:
        print(str(e))
    return

def template_queue(path, base_dir="/var/lib/docker/data/"):
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
    # needed to preserve case sensitive options
    config.optionxform=str

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

    template_dir = base_dir+"templates/"
    vent_dir = "/vent/"
    if base_dir != "/var/lib/docker/data/":
        vent_dir = base_dir
    # check for template type
    try:
        template = path.split("/")[-1]
        if template == "modes.template":
            # kill all running containers, just in case, then start the core
            # !! TODO perhaps also start collectors and viz if they were previously running?
            # check if the container is this one and kill it last!
            hostname = os.environ.get('HOSTNAME')
            current_container = hostname
            core_containers = c.containers(all=True)
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
                os.system('python2.7 '+vent_dir+'template_parser.py core start')
            # !! TODO failing, so commenting out for now
            #c.restart(current_container)
        elif template == "core.template":
            # check if the container is this one and kill it last!
            hostname = os.environ.get('HOSTNAME')
            current_container = hostname
            # check if active/passive are disabled, and kill/remove containers
            if os.path.isfile(template_dir+'core.template'):
                config.read(template_dir+'core.template')
            local_collection = []
            passive = False
            active = False
            if config.has_section("local-collection") and config.options("local-collection"):
                local_collection = config.options("local-collection")
            for collector in local_collection:
                val = config.get("local-collection", collector)
                if collector == "passive" and val == "on":
                    passive = True
                if collector == "active" and val == "on":
                    active = True
            if not passive:
                passive_containers = c.containers(all=True, filters={'name':"passive"})
                for cont in passive_containers:
                    try:
                        c.kill(cont['Id'])
                        c.remove_container(cont['Id'])
                    except Exception as e:
                        pass
            if not active:
                active_containers = c.containers(all=True, filters={'name':"active"})
                for cont in active_containers:
                    try:
                        c.kill(cont['Id'])
                        c.remove_container(cont['Id'])
                    except Exception as e:
                        pass

            # kill and remove core containers
            core_containers = c.containers(quiet=True, all=True, filters={'name':"core"})
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
                os.system('python2.7 '+vent_dir+'template_parser.py core start')
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
                os.system('python2.7 '+vent_dir+'template_parser.py active start')
            passive_containers = c.containers(quiet=True, all=True, filters={'name':"passive"})
            for cont in passive_containers:
                try:
                    c.kill(cont['Id'])
                    c.remove_container(cont['Id'])
                except Exception as e:
                    pass
            if len(passive_containers) > 0:
                os.system('python2.7 '+vent_dir+'template_parser.py passive start')
        elif template == "visualization.template":
            viz_containers = c.containers(quiet=True, all=True, filters={'name':"visualization"})
            for cont in viz_containers:
                try:
                    c.kill(cont['Id'])
                    c.remove_container(cont['Id'])
                except Exception as e:
                    pass
            if len(viz_containers) > 0:
                os.system('python2.7 '+vent_dir+'template_parser.py visualization start')
        else:
            pass
            # plugin
    except Exception as e:
        print(str(e))
    return
