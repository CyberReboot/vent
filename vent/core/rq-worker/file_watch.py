def file_queue(path, base_dir="/var/lib/docker/data/"):
    """
    Processes files that have been added from the rq-worker, and tells
    vent-management to start plugins that match the mime type for the new file.
    """
    import ConfigParser
    import magic
    import os
    import time

    # TODO rewrite
    #from docker import Client
    #from docker.utils.types import LogConfig
    #
    #c = Client(base_url='unix://var/run/docker.sock')
    #
    ## first some cleanup
    #containers = c.containers(quiet=True, all=True, filters={'status':"exited"})
    #for cont in containers:
    #    try:
    #        # will only remove containers that aren't running
    #        c.remove_container(cont['Id'])
    #    except Exception as e:
    #        pass

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
