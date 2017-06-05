def file_queue(path, template_path="/vent/"):
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

    status = (True, None)
    # get the correct path for binding
    vent_config = ConfigParser.RawConfigParser()
    vent_config.optionxform=str
    vent_config.read(template_path+'vent.cfg')
    if vent_config.has_section('main') and vent_config.has_option('main', 'files'):
        files = vent_config.get('main', 'files')
    else:
        files = '/'

    try:
        hostname, path = path.split('_', 1)
        path = path.replace('/files', files, 1)

        # read in configuration of plugins to get the ones that should run against the path.
        # TODO error checking and catching...
        config = ConfigParser.RawConfigParser()
        config.optionxform=str
        config.read(template_path+'plugin_manifest.cfg')
        sections = config.sections()
        for section in sections:
            t_path = config.get(section, 'path')
            t_path = template_path+'plugins/' + t_path.split('/plugins/')[1] + "/vent.template"
            t_config = ConfigParser.RawConfigParser()
            t_config.optionxform=str
            t_config.read(t_path)
            if t_config.has_section('settings') and t_config.has_option('settings', 'ext_types'):
                ext_types = t_config.get('settings', 'ext_types').split(',')
                for ext_type in ext_types:
                    if path.endswith(ext_type):
                        images.append(config.get(section, 'image_name'))

        # TODO add connections to syslog, labels, and file path etc.
        # TODO get syslog address rather than hardcode
        # TODO get group and name for tag
        # TODO add rw volume for plugin output to be plugin input
        labels = {'vent-plugin':'', 'file':path}
        log_config = {'type':'syslog',
                      'config': {'syslog-address':'tcp://0.0.0.0:514',
                                 'syslog-facility':'daemon',
                                 'tag':path.rsplit('.', 1)[-1]}}
        volumes = {path:{'bind':path, 'mode':'ro'}}

        # start containers
        for image in images:
            d_client.containers.run(image=image,
                                    command=path,
                                    labels=labels,
                                    detach=True,
                                    log_config=log_config,
                                    volumes=volumes)
        status = (True, images)
    except Exception as e:
        status = (False, None)

    return status
