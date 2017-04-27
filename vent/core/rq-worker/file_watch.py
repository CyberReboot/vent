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

    images = []

    # get the correct path for binding
    vent_config = Template(template='/vent/vent.cfg')
    files = vent_config.option('main', 'files')
    hostname, path = path.split('_', 1)
    path = path.replace('/files', files, 1)

    # read in configuration of plugins to get the ones that should run against the path.
    # TODO error checking and catching...
    config = ConfigParser.RawConfigParser()
    config.optionxform=str
    config.read('/vent/plugin_manifest.cfg')
    sections = config.sections()
    for section in sections:
        template_path = config.get(section, 'path')
        template_path = '/vent/plugins/' + template_path.split('/plugins/')[1] + "/vent.template"
        t_config = ConfigParser.RawConfigParser()
        t_config.optionxform=str
        t_config.read(template_path)
        if t_config.has_section('settings') and t_config.has_option('settings', 'ext_types'):
            ext_types = t_config.get('settings', 'ext_types').split(',')
            for ext_type in ext_types:
                if path.endswith(ext_type):
                    images.append(config.get(section, 'image_name'))

    # TODO add connections to syslog, labels, and file path etc.
    # TODO get syslog address rather than hardcode
    # TODO get group and name for tag
    # TODO add rw volume for plugin output to be plugin input
    log_config = {'type':'syslog', 'config': {'syslog-address':'tcp://0.0.0.0:514', 'syslog-facility':'daemon', 'tag':'foo'}}
    volumes = {path:{'bind':path, 'mode':'ro'}}

    # start containers
    for image in images:
        d_client.containers.run(image=image, command=path, detach=True, log_config=log_config, volumes=volumes)

    return images
