def template_queue(path):
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
        except:
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
                    except:
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
                except:
                    pass
            if len(active_containers) > 0:
                os.system('python2.7 /vent/template_parser.py active start')
            passive_containers = c.containers(quiet=True, all=True, filters={'name':"passive"})
            for cont in passive_containers:
                try:
                    c.kill(cont['Id'])
                    c.remove_container(cont['Id'])
                except:
                    pass
            if len(passive_containers) > 0:
                os.system('python2.7 /vent/template_parser.py passive start')
        elif template == "visualization.template":
            viz_containers = c.containers(quiet=True, all=True, filters={'name':"visualization"})
            for cont in viz_containers:
                try:
                    c.kill(cont['Id'])
                    c.remove_container(cont['Id'])
                except:
                    pass
            if len(viz_containers) > 0:
                os.system('python2.7 /vent/template_parser.py visualization start')
        else:
            pass
            # plugin
    except:
        pass
    return
