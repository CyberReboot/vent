def file_queue(path, template_path="/vent/"):
    """
    Processes files that have been added from the rq-worker, starts plugins
    that match the mime type for the new file.
    """
    import ConfigParser
    import docker
    import json
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
        # keep track of images that failed getting configurations for
        failed_images = set()
        config = ConfigParser.RawConfigParser()
        config.optionxform = str
        config.read(template_path+'plugin_manifest.cfg')
        sections = config.sections()
        for section in sections:
            image_name = config.get(section, 'image_name')
            # doesn't matter if it's a repository or registry because both in manifest
            if config.has_option(section, 'service'):
                try:
                    options_dict = json.loads(config.get(section, 'service'))
                    for option in options_dict:
                        value = options_dict[option]
                        labels[option] = value
                except Exception as e:   # pragma: no cover
                    failed_images.add(image_name)
                    status = (False, str(e))
            if config.has_option(section, 'settings'):
                try:
                    options_dict = json.loads(config.get(section, 'settings'))
                    for option in options_dict:
                        if option == 'ext_types':
                            ext_types = options_dict[option].split(',')
                            for ext_type in ext_types:
                                if path.endswith(ext_type):
                                    images.append(image_name)
                                    configs[image_name] = {}
                except Exception as e:   # pragma: no cover
                    failed_images.add(image_name)
                    status = (False, str(e))
            if config.has_option(section, 'gpu') and image_name in configs:
                try:
                    options_dict = json.loads(config.get(section, 'gpu'))
                    if 'enabled' in options_dict:
                        enabled = options_dict['enabled']
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
                                failed_images.add(image_name)
                                status = (False, str(e))
                except Exception as e:   # pragma: no cover
                    failed_images.add(image_name)
                    status = (False, str(e))

        # TODO add connections to syslog, labels, and file path etc.
        # TODO get syslog address rather than hardcode
        # TODO get group and name for tag
        # TODO add rw volume for plugin output to be plugin input
        log_config = {'type': 'syslog',
                      'config': {'syslog-address': 'tcp://0.0.0.0:514',
                                 'syslog-facility': 'daemon',
                                 'tag': path.rsplit('.', 1)[-1]}}
        volumes = {path: {'bind': path, 'mode': 'rw'}}

        # start containers
        for image in images:
            if image not in failed_images:
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
        if not failed_images:
            status = (True, images)
    except Exception as e:  # pragma: no cover
        status = (False, str(e))

    return status
