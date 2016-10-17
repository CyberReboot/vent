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
    vent_dir = "/vent/"
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
            # check file extensions
            ext_types = []
            try:
                config = ConfigParser.RawConfigParser()
                # needed to preserve case sensitive options
                config.optionxform=str
                if os.path.isfile(template_dir+plugin+'.template'):
                    config.read(template_dir+plugin+'.template')
                if config.has_section("service") and config.has_option("service", "ext_types"):
                    ext_types = config.get("service", "ext_types").split(",")
            except Exception as e:
                print(str(e))
            if len(mime_types) == 0 or file_mime in mime_types or path.split(".", -1)[-1] in ext_types:
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
    the rq-worker. Then, removes exited containers, kills and removes disabled containers,
    and starts/restarts enabled containers. Only restarts enabled containers which were
    running at the time of the configuration change.
    """
    import ast
    import os
    import sys
    import time

    import ConfigParser
    config = ConfigParser.RawConfigParser()
    # needed to preserve case sensitive options
    config.optionxform=str

    from docker import Client
    from docker.utils.types import LogConfig
    from subprocess import check_output
    c = Client(base_url='unix://var/run/docker.sock')

    try:
        # keep track of running containers to restart
        running_containers = c.containers()

        # first some cleanup
        containers = c.containers(quiet=True, all=True, filters={'status':"exited"})
        for cont in containers:
            try:
                # will only remove containers that aren't running
                c.remove_container(cont['Id'])
            except Exception as e:
                pass
        try:
            data_dir = "/scripts/"
            if base_dir != "/var/lib/docker/data/":
                data_dir = base_dir
            enabled, disabled = ast.literal_eval(check_output("python2.7 "+data_dir+"info_tools/get_status.py enabled -b "+base_dir, shell=True))
        except Exception as e:
            pass
        # remove disabled running containers
        for container in containers:
            for name in container["Names"]:
                if name in disabled:
                    try:
                        c.kill(container["Id"])
                        c.remove_container(container["Id"])
                        continue
                    except Exception as e:
                        pass

        core_containers = c.containers(all=True, filters={'name':"core-"})

        # remove core containers, so when restarted, behavior matches current configuration
        for container in core_containers:
            try:
                if container["Status"] == "exited":
                    c.remove_container(container["Id"])
                elif container["Id"].startswith(os.environ.get('HOSTNAME')):
                    # skip this container until the end
                    this_container = container["Id"]
                else:
                    c.kill(container["Id"])
                    c.remove_container(container["Id"])
            except Exception as e:
                pass

        # restart this container last
        try:
            c.kill(this_container)
            c.remove_container(this_container)
        except Exception as e:
            pass
        # start enabled containers
        data_dir = "/vent/"
        if base_dir != "/var/lib/docker/data/":
            data_dir = base_dir
        os.system('python2.7 '+data_dir+'template_parser.py core start')

        active_started = False
        passive_started = False
        vis_started = False

        for container in running_containers:
            # usually containers have one name, but container["Names"] is a list, so we have to be sure
            for name in container["Names"]:
                if active_started and passive_started and vis_started:
                    break
                elif "active-" in name and not active_started:
                    os.system('python2.7 '+base_dir+'template_parser.py active start')
                    active_started = True
                elif "passive-" in name and not passive_started:
                    os.system('python2.7 '+base_dir+'template_parser.py passive start')
                    passive_started = True
                elif "visualization-" in name and not vis_started:
                    os.system('python2.7 '+base_dir+'template_parser.py visualization start')
                    vis_started = True
                else:
                    pass
    except Exception as e:
        pass
    return
