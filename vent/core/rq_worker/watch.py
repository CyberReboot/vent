def gpu_queue(options):
    """
    Queued up containers waiting for GPU resources
    """
    import docker
    import json
    import os
    import time

    from vent.helpers.meta import GpuUsage

    status = (False, None)
    if (os.path.isfile("/root/.vent/vent.cfg") and os.path.isfile("/root/.vent/plugin_manifest.cfg")):
        path_dir = "/root/.vent"
    else:
        path_dir = "/vent"

    print("gpu queue", str(options))
    print("gpu queue", str(GpuUsage(base_dir=path_dir+"/",
                                    meta_dir=path_dir)))

    options = json.loads(options)
    configs = options['configs']
    gpu_options = configs['gpu_options']
    devices = []

    # device specified, remove all other devices
    if 'device' in gpu_options:
        dev = '/dev/nvidia' + gpu_options['device'] + ':/dev/nvidia'
        dev += gpu_options['device'] + ':rwm'
        if 'devices' in configs:
            d = list(configs['devices'])
            for device in d:
                if any(str.isdigit(str(char)) for char in device):
                    if dev == device:
                        devices.append(device)
                    else:
                        configs['devices'].remove(device)
    else:
        d = configs['devices']
        for device in d:
            if any(str.isdigit(str(char)) for char in device):
                devices.append(device)

    # check if devices is still an empty list
    if not devices:
        status = (False, "no valid devices match the requested device")
        print(str(status))
        return status

    mem_needed = 0
    dedicated = False
    # need a gpu to itself
    if ('dedicated' in configs['gpu_options'] and
       configs['gpu_options']['dedicated'] == 'yes'):
        dedicated = True
    if 'mem_mb' in configs['gpu_options']:
        # TODO input error checking
        mem_needed = int(configs['gpu_options']['mem_mb'])

    print("mem_needed: ", mem_needed)
    print("dedicated: ", dedicated)
    device = None
    while not device:
        usage = GpuUsage(base_dir=path_dir+"/", meta_dir=path_dir)

        if usage[0]:
            usage = usage[1]
        else:
            return usage
        print(usage)
        # {"device": "0",
        #  "mem_mb": "1024",
        #  "dedicated": "yes",
        #  "enabled": "yes"}
        for d in devices:
            dev = str(d.split(":")[0].split('nvidia')[1])
            print(dev)
            # if the device is already dedicated, can't be used
            dedicated_gpus = usage['vent_usage']['dedicated']
            is_dedicated = False
            for gpu in dedicated_gpus:
                if dev in gpu:
                    is_dedicated = True
            print("is_dedicated: ", is_dedicated)
            if not is_dedicated:
                ram_used = 0
                if dev in usage['vent_usage']['mem_mb']:
                    ram_used = usage['vent_usage']['mem_mb'][dev]
                # check for vent usage/processes running
                if (dedicated and
                   dev not in usage['vent_usage']['mem_mb'] and
                   mem_needed <= usage[int(dev)]['global_memory'] and
                   not usage[int(dev)]['processes']):
                    device = dev
                # check for ram constraints
                elif mem_needed <= (usage[int(dev)]['global_memory'] - ram_used):
                    device = dev

        # TODO make this sleep incremental up to a point, potentially kill
        #      after a set time configured from vent.cfg, outputting as it goes
        time.sleep(1)

    # lock jobs to a specific gpu (no shared GPUs for a single process) this is
    # needed to calculate if memory requested (but not necessarily in use)
    # would become oversubscribed

    # store which device was mapped
    options['labels']['vent.gpu.device'] = device
    gpu_device = '/dev/nvidia' + device + ':/dev/nvidia' + device + ':rwm'
    if 'devices' in configs:
        d = configs['devices']
        for dev in d:
            if any(str.isdigit(str(char)) for char in dev):
                if gpu_device != dev:
                    configs['devices'].remove(dev)

    try:
        d_client = docker.from_env()
        del options['configs']
        del configs['gpu_options']
        params = options.copy()
        params.update(configs)
        d_client.containers.run(**params)
        status = (True, None)
    except Exception as e:  # pragma: no cover
        status = (False, str(e))

    print(str(status))
    return status


def file_queue(path, template_path="/vent/", r_host="redis"):
    """
    Processes files that have been added from the rq-worker, starts plugins
    that match the mime type for the new file.
    """
    import configparser
    import ast
    import docker
    import json
    import requests
    import os
    import sys

    from redis import Redis
    from rq import Queue
    from subprocess import check_output, Popen, PIPE
    from string import punctuation
    from vent.helpers.logs import Logger

    status = (True, None)
    images = []
    configs = {}
    logger = Logger(__name__)

    if (os.path.isfile("/root/.vent/vent.cfg") and os.path.isfile("/root/.vent/plugin_manifest.cfg")):
        template_path = "/root/.vent/"

    try:
        d_client = docker.from_env()

        # get the correct path for binding
        vent_config = configparser.ConfigParser(interpolation=None)
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
        path_copy = path

        # read in configuration of plugins to get the ones that should run
        # against the path.
        # keep track of images that failed getting configurations for
        failed_images = set()
        config = configparser.ConfigParser(interpolation=None)
        config.optionxform = str
        print("Path to manifest: "+ template_path+'plugin_manifest.cfg')
        config.read(template_path+'plugin_manifest.cfg')
        sections = config.sections()
        name_maps = {}
        orig_path_d = {}
        path_cmd = {}
        labels_d = {}

        # get all name maps
        for section in sections:
            link_name = config.get(section, 'link_name')
            image_name = config.get(section, 'image_name')
            name_maps[link_name] = image_name.replace(':', '-').replace('/', '-')

        for section in sections:
            path = path_copy
            orig_path = ''
            repo = config.get(section, 'repo')
            t_type = config.get(section, 'type')
            labels = {'vent-plugin': '', 'file': path, 'vent.section': section, 'vent.repo': repo, 'vent.type': t_type}
            image_name = config.get(section, 'image_name')
            link_name = config.get(section, 'link_name')
            # doesn't matter if it's a repository or registry because both in manifest
            if config.has_option(section, 'groups'):
                if 'replay' in config.get(section, 'groups'):
                    try:
                        # read the vent.cfg file to grab the network-mapping
                        # specified. For replay_pcap
                        n_name = 'network-mapping'
                        n_map = []
                        if vent_config.has_section(n_name):
                            # make sure that the options aren't empty
                            if vent_config.options(n_name):
                                options = vent_config.options(n_name)
                                for option in options:
                                    if vent_config.get(n_name, option):
                                        n_map.append(vent_config.get(
                                            n_name, option))
                                orig_path = path
                                path = str(n_map[0]) + " " + path
                    except Exception as e:  # pragma: no cover
                        failed_images.add(image_name)
                        status = (False, str(e))
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
                            dir_pieces = directory.split('/')
                            dir_check = dir_pieces
                            for dir_piece in dir_pieces:
                                if 'UTC' in dir_piece:
                                    dir_check = dir_piece
                            if tool.replace(' ', '-') in dir_check:
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
            if image_name in configs:
                if config.has_option(section, 'docker'):
                    try:
                        options_dict = ast.literal_eval(config.get(section, 'docker'))
                        for option in options_dict:
                            try:
                                configs[image_name][option] = ast.literal_eval(options_dict[option])
                            except Exception as e:  # pragma: no cover
                                configs[image_name][option] = options_dict[option]
                        if 'links' in configs[image_name]:
                            for link in configs[image_name]['links']:
                                if link in name_maps:
                                    configs[image_name]['links'][name_maps[link]] = configs[image_name]['links'].pop(link)
                        # TODO network_mode
                        # TODO volumes_from
                        # TODO external services
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
                            labels['vent.gpu'] = 'yes'
                            if 'dedicated' in options_dict:
                                labels['vent.gpu.dedicated'] = options_dict['dedicated']
                            if 'device' in options_dict:
                                labels['vent.gpu.device'] = options_dict['device']
                            if 'mem_mb' in options_dict:
                                labels['vent.gpu.mem_mb'] = options_dict['mem_mb']
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
                                # grab the default gateway
                                try:
                                    route = Popen(('/sbin/ip', 'route'),
                                                  stdout=PIPE)
                                    host = check_output(('awk', '/default/ {print$3}'),
                                                        stdin=route.stdout).strip().decode("utf-8")
                                    route.wait()
                                except Exception as e:  # pragma no cover
                                    logger.error("Default gateway "
                                                 "went wrong " + str(e))
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
                                print("Failure with nvidia-docker-plugin: " +
                                      str(e))
                except Exception as e:   # pragma: no cover
                    failed_images.add(image_name)
                    status = (False, str(e))
                    print("Unable to process gpu options: " + str(e))
            path_cmd[image_name] = path
            orig_path_d[image_name] = orig_path
            labels_d[image_name] = labels

        # TODO get syslog address rather than hardcode
        # TODO add group label
        # TODO get group and name for syslog tag
        log_config = {'type': 'syslog',
                      'config': {'syslog-address': 'tcp://0.0.0.0:514',
                                 'syslog-facility': 'daemon',
                                 'tag': '{{.Name}}/{{.ID}}/'+path.rsplit('.', 1)[-1]}}

        # setup gpu queue
        can_queue_gpu = True
        try:
            q = Queue(connection=Redis(host=r_host), default_timeout=86400)
        except Exception as e:  # pragma: no cover
            can_queue_gpu = False
            print("Unable to connect to redis: " + str(e))

        # start containers
        for image in images:
            if image not in failed_images:
                orig_path = orig_path_d[image]
                labels = labels_d[image]

                if orig_path:
                    # replay_pcap is special so we can't bind it like normal
                    # since the plugin takes in an additional argument
                    dir_path = orig_path.rsplit('/', 1)[0]
                else:
                    dir_path = path.rsplit('/', 1)[0]
                volumes = {dir_path: {'bind': dir_path, 'mode': 'rw'}}

                if 'volumes' in configs[image]:
                    for volume in volumes:
                        configs[image]['volumes'][volume] = volumes[volume]
                else:
                    configs[image]['volumes'] = volumes

                if 'vent.gpu' in labels and labels['vent.gpu'] == 'yes':
                    if can_queue_gpu:
                        # queue up containers requiring a gpu
                        q_str = json.dumps({'image': image,
                                            'command': path_cmd[image],
                                            'labels': labels,
                                            'detach': True,
                                            'log_config': log_config,
                                            'configs': configs[image]})
                        q.enqueue('watch.gpu_queue', q_str, ttl=2592000)
                    else:
                        failed_images.add(image)
                else:
                    if 'gpu_options' in configs[image]:
                        del configs[image]['gpu_options']
                    d_client.containers.run(image=image,
                                            command=path_cmd[image],
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
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
        print("Failed to process job: " + str(e))

    print(str(status))
    return status
