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
        except:
            pass

    responses = {}

    template_dir = "/data/templates/"
    plugins_dir = "/data/plugins/"
    try:
        config.read(template_dir+'modes.template')
        plugin_array = config.options("plugins")
        plugins = {}
        for plug in plugin_array:
            if plug != "core" and plug != "visualization" and plug != "collectors":
                plugins[plug] = config.get("plugins", plug)
        t = []
        for plugin in plugins:
            if plugins[plugin] == 'all':
                tools = [ name for name in os.listdir(plugins_dir+plugin) if os.path.isdir(os.path.join(plugins_dir+plugin, name)) ]
                for tool in tools:
                    t.append(plugin+'/'+tool)
            else:
                for tool in plugins[plugin].split(","):
                    t.append(plugin+'/'+tool)

        container_count = 0
        container_max = 50
        try:
            config.read(template_dir+'core.template')
            container_max = int(config.get("active-containers", "count"))
        except:
            pass
        for image in t:
            # check resources before creating container
            # wait until there are resources available
            container_count = len(c.containers(filters={'status':'running'}))
            while container_count >= container_max:
                time.sleep(5)
                container_count = len(c.containers(filters={'status':'running'}))
            # for plugin, create container and start it
            # !! TODO read params for create_container from the templates!
            try:
                config.read(template_dir+'core.template')
                locally_active = config.options("locally-active")
                syslog_host = "localhost"
                if "aaa-syslog" in locally_active:
                    if config.get("locally-active", "aaa-syslog") == "off":
                        external_array = config.options("external")
                        if "aaa-syslog_host" in external_array:
                            syslog_host = config.get("external", "aaa-syslog_host")
                flag = 0
                if "aaa-rabbitmq" in locally_active:
                    if config.get("locally-active", "aaa-rabbitmq") == "off":
                        external_array = config.options("external")
                        if "aaa-rabbitmq_host" in external_array:
                            rabbitmq_host = config.get("external", "aaa-rabbitmq_host")
                            flag = 1
                hc = None
                if flag:
                    hc = c.create_host_config(extra_hosts={"rabbitmq":rabbitmq_host}, binds=["/pcaps:/pcaps:ro"], log_config={'type': LogConfig.types.SYSLOG, 'config': {"tag":"{{.ImageName}}/{{.Name}}/{{.ID}}","syslog-address":"tcp://"+syslog_host}})
                else:
                    hc = c.create_host_config(links={"core-aaa-rabbitmq":"rabbitmq"}, binds=["/pcaps:/pcaps:ro"], log_config={'type': LogConfig.types.SYSLOG, 'config': {"tag":"{{.ImageName}}/{{.Name}}/{{.ID}}","syslog-address":"tcp://"+syslog_host}})
                container = c.create_container(image=image, host_config=hc, volumes=["/pcaps"], environment=["PYTHONUNBUFFERED=0"], tty=True, stdin_open=True, command=path)
                response = c.start(container=container.get('Id'))
                responses[image] = response
            except:
                pass
    except:
        pass
    return responses
