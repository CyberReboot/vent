def file_queue(path, template_path="/vent/"):
    """
    Processes files that have been added from the rq-worker, starts plugins
    that match the mime type for the new file.
    """
    import ConfigParser
    import docker
    import requests

    from subprocess import check_output, Popen, PIPE

    status = (True, None)
    images = []
    configs = {}

    try:
        d_client = docker.from_env()

        # get the correct path for binding
        vent_config = ConfigParser.RawConfigParser()
        vent_config.optionxform = str
        vent_config.read(template_path+'vent.cfg')
        if (vent_config.has_section('main') and
           vent_config.has_option('main', 'files')):
            files = vent_config.get('main', 'files')
        else:
            files = '/'

        _, path = path.split('_', 1)
        path = path.replace('/files', files, 1)

        labels = {'vent-plugin': '', 'file': path}
        # read in configuration of plugins to get the ones that should run
        # against the path.
        config = ConfigParser.RawConfigParser()
        config.optionxform = str
        config.read(template_path+'plugin_manifest.cfg')
        sections = config.sections()
        for section in sections:
            image_name = config.get(section, 'image_name')
            t_type = config.get(section, 'type')
            if t_type == 'repository':
                t_path = config.get(section, 'path')
                t_p = template_path + 'plugins/'
                t_path = t_p + t_path.split('/plugins/')[1] + "/vent.template"
                t_config = ConfigParser.RawConfigParser()
                t_config.optionxform = str
                t_config.read(t_path)
                if t_config.has_section('service'):
                    options = t_config.options('service')
                    for option in options:
                        value = t_config.get('service', option)
                        labels[option] = value
                if (t_config.has_section('settings') and
                   t_config.has_option('settings', 'ext_types')):
                    ext_types = t_config.get('settings',
                                             'ext_types').split(',')
                    for ext_type in ext_types:
                        if path.endswith(ext_type):
                            images.append(image_name)
                            configs[image_name] = {}
                if t_config.has_section('gpu') and image_name in configs:
                    if t_config.has_option('gpu', 'enabled'):
                        enabled = t_config.get('gpu', 'enabled')
                        if enabled == 'yes':
                            route = Popen(('/sbin/ip', 'route'), stdout=PIPE)
                            h = check_output(('awk', '/default/ {print $3}'),
                                             stdin=route.stdout)
                            route.wait()
                            host = h.strip()
                            nd_url = 'http://' + host + ':3476/v1.0/docker/cli'
                            params = {'vol': 'nvidia_driver'}
                            try:
                                r = requests.get(nd_url, params=params)
                                if r.status_code == 200:
                                    options = r.text.split()
                                    for option in options:
                                        if option.startswith('--volume-driver='):
                                            configs[image_name]['volume_driver'] = option.split("=", 1)[1]
                                        elif option.startswith('--volume='):
                                            vol = option.split("=", 1)[1].split(":")
                                            if 'volumes' in configs[image_name]:
                                                # !! TODO handle if volumes is a list
                                                configs[image_name]['volumes'][vol[0]] = {'bind': vol[1],
                                                                                          'mode': vol[2]}
                                            else:
                                                configs[image_name]['volumes'] = {vol[0]:
                                                                                  {'bind': vol[1],
                                                                                   'mode': vol[2]}}
                                        elif option.startswith('--device='):
                                            dev = option.split("=", 1)[1]
                                            if 'devices' in configs[image_name]:
                                                configs[image_name]['devices'].append(dev +
                                                                                      ":" +
                                                                                      dev +
                                                                                      ":rwm")
                                            else:
                                                configs[image_name]['devices'] = [dev + ":" + dev + ":rwm"]
                                        else:
                                            # unable to parse option provided by
                                            # nvidia-docker-plugin
                                            pass
                            except Exception as e:  # pragma: no cover
                                pass
            elif t_type == 'registry':
                # !! TODO deal with images not from a repo
                pass

        # TODO add connections to syslog, labels, and file path etc.
        # TODO get syslog address rather than hardcode
        # TODO get group and name for tag
        # TODO add rw volume for plugin output to be plugin input
        log_config = {'type': 'syslog',
                      'config': {'syslog-address': 'tcp://0.0.0.0:514',
                                 'syslog-facility': 'daemon',
                                 'tag': path.rsplit('.', 1)[-1]}}
        volumes = {path: {'bind': path, 'mode': 'ro'}}

        # start containers
        for image in images:
            # TODO check for availability of gpu(s),
            #      otherwise queue it up until it's
            #      available
            if 'volumes' in configs[image]:
                for volume in volumes:
                    configs[image]['volumes'][volume] = volumes[volume]
            else:
                configs[image]['volumes'] = volumes
            d_client.containers.run(image=image,
                                    command=path,
                                    labels=labels,
                                    detach=True,
                                    log_config=log_config,
                                    **configs[image])
        status = (True, images)
    except Exception as e:  # pragma: no cover
        status = (False, str(e))

    return status
