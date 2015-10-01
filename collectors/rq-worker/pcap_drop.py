def pcap_queue(path):
    import os

    import ConfigParser
    config = ConfigParser.RawConfigParser()

    from docker import Client
    c = Client(base_url='unix://var/run/docker.sock')

    responses = {}

    template_dir = "/data/templates/"
    plugins_dir = "/data/plugins/"
    try:
        config.read(template_dir+'modes.template')
        plugin_array = config.options("plugins")
        plugins = {}
        for plug in plugin_array:
            if plug != "collectors" and plug != "visualization":
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

        for image in t:
            # for plugin, create container and start it
            # !! TODO read params for create_container from the templates!
            try:
                container = c.create_container(image=image, volumes=["/pcaps"], environment=["PYTHONUNBUFFERED=0"], tty=True, stdin_open=True, command=path)
                response = c.start(container=container.get('Id'), binds=["/pcaps:/pcaps:ro"], links={"collectors-rabbitmq":"rabbitmq"})
                responses[image] = response
            except:
                pass
    except:
        pass
    return responses
