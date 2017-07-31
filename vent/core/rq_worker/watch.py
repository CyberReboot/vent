def gpu_queue(options):
    """
    Queued up containers waiting for GPU resources
    """
    import docker
    import json

    from vent.helpers.meta import GpuUsage

    status = (False, None)

    # device specified, remove all other devices
    if 'device' in options['gpu_options']:
        dev = '/dev/nvidia' + options['gpu_options']['device'] + ':rwm'
        if 'devices' in options:
            devices = option['devices']
            for device in devices:
                if any(str.isdigit(char) for char in device):
                    if dev is not device:
                        option['devices'].remove(device)

    print("gpu queue", str(options))
    print("gpu queue", str(GpuUsage()))

    # TODO overriding until this is working
    # wait = True
    wait = False

    while wait:
        usage = GpuUsage()
        check = 0
        # TODO check if GPUs are available for the set restrictions
        # no restrictions set
        if len(options['gpu_options']) == 1:
            check = 3
        else:
            # check if dev is available
            if 'device' in options['gpu_options']:
                if not usage[options['gpu_options']['device']]['processes']:
                    check += 1
            else:
                check += 1

            # TODO mem_mb needed available

            # TODO dedicated

        # TODO check if gpus are available
        if check == 3:
            wait = False
    try:
        d_client = docker.from_env()
        options = json.loads(options)
        configs = options['configs']
        gpu_options = configs['gpu_options']
        del options['configs']
        del configs['gpu_options']
        params = options.copy()
        params.update(configs)
        print(str(params))
        d_client.containers.run(**params)
        status = (True, None)
    except Exception as e:  # pragma: no cover
        status = (False, str(e))

    print(str(status))
    return status


def file_queue(path, template_path="/vent/"):
    """
    Processes files that have been added from the rq-worker, starts plugins
    that match the mime type for the new file.
    """
    import ConfigParser
    import docker
    import json
    import requests
    import os

    from redis import Redis
    from rq import Queue
    from subprocess import check_output, Popen, PIPE
    from string import punctuation

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

        # deal with ~
        files = os.path.expanduser(files)

        chars = set(punctuation)
        chars.discard('/')
        chars.discard('_')
        chars.discard('-')
        file_name = ''
        # escape any funky symbols to allow users FREEDOM of directory name
        for char in files:
            if char in chars:
                if char == '\\':
                    file_name += '\\' + char
                else:
                    file_name += '\\\\' + char
            else:
                file_name += char

        files = file_name
        _, path = path.split('_', 1)
        directory = path.rsplit('/', 1)[0]
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
                    in_base = directory == '/files'
                    # process base by default
                    process_file = in_base
                    # check if this tool shouldn't process the base by default
                    if 'process_base' in options_dict:
                        if options_dict['process_base'] == 'no':
                            process_file = False
                    # check if this tool should look at subdirs created by
                    # other tools' output
                    if 'process_from_tool' in options_dict and not in_base:
                        for tool in options_dict['process_from_tool'].split(','):
                            if tool.replace(' ', '-') in directory:
                                process_file = True
                    if 'ext_types' in options_dict and process_file:
                        ext_types = options_dict['ext_types'].split(',')
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
                            configs[image_name]['gpu_options'] = options_dict
                            if 'labels' in configs[image_name]:
                                configs[image_name]['labels']['vent.gpu'] = 'yes'
                            else:
                                configs[image_name]['labels'] = {'vent.gpu': 'yes'}
                            port = ''
                            host = ''
                            if (vent_config.has_section('nvidia-docker-plugin') and
                               vent_config.has_option('nvidia-docker-plugin', 'port')):
                                port = vent_config.get('nvidia-docker-plugin', 'port')
                            else:
                                port = '3476'
                            if (vent_config.has_section('nvidia-docker-plugin') and
                               vent_config.has_option('nvidia-docker-plugin', 'host')):
                                host = vent_config.get('nvidia-docker-plugin', 'host')
                            else:
                                route = Popen(('/sbin/ip', 'route'), stdout=PIPE)
                                h = check_output(('awk', '/default/ {print $3}'),
                                                 stdin=route.stdout)
                                route.wait()
                                host = h.strip()
                            nd_url = 'http://' + host + ':' + port + '/v1.0/docker/cli'
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
        dir_path = path.rsplit('/', 1)[0]
        volumes = {dir_path: {'bind': dir_path, 'mode': 'rw'}}

        # setup gpu queue
        can_queue_gpu = True
        try:
            q = Queue(connection=Redis(host='redis'), default_timeout=86400)
        except Exception as e:  # pragma: no cover
            can_queue_gpu = False

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
                if ('labels' in configs[image] and
                   'vent.gpu' in configs[image]['labels'] and
                   configs[image]['labels']['vent.gpu'] == 'yes'):
                    if can_queue_gpu:
                        # queue up containers requiring a gpu
                        q_str = json.dumps({'image': image,
                                            'command': path,
                                            'labels': labels,
                                            'detach': True,
                                            'log_config': log_config,
                                            'configs': configs[image]})
                        q.enqueue('watch.gpu_queue', q_str, ttl=2592000)
                    else:
                        failed_images.add(image)
                else:
                    d_client.containers.run(image=image,
                                            command=path,
                                            labels=labels,
                                            detach=True,
                                            log_config=log_config,
                                            **configs[image])
        if failed_images:
            status = (False, failed_images)
        else:
            status = (True, images)
    except Exception as e:  # pragma: no cover
        status = (False, str(e))

    return status
