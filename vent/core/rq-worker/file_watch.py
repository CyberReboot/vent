def file_queue(path):
    """
    Processes files that have been added from the rq-worker, starts plugins
    that match the mime type for the new file.
    """
    import ConfigParser
    import docker
    import magic
    import os
    import time

    d_client = docker.from_env()

    containers = []
    # TODO read in configuration of plugins to get the ones that should run against the path.
    config = ConfigParser.RawConfigParser()
    config.optionxform=str
    config.read('/vent/plugin_manifest.cfg')
    sections = config.sections()
    for section in sections:
        template_path = config.get(section, 'path')
        template_path = '/vent/plugins/' + template_path.split('/plugins/')[1] + "/vent.template"
        t_config = ConfigParser.RawConfigParser()
        t_config.optionxform=str
        t_config.read('/vent/plugin_manifest.cfg')
        t_config.read(template_path)
        if t_config.has_section('settings'):
            if t_config.has_option('settings', 'ext_types'):
                ext_types = t_config.get('settings', 'ext_types')
                ext_types = ext_types.split(',')
                for ext_type in ext_types:
                    if path.endswith(ext_type):
                        containers.append(section)

    # TODO add connections to syslog, and file path etc.

    # TODO start containers

    #d_client.containers.run()

    return containers
