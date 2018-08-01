import datetime
import json
import math
import multiprocessing
import os
import platform
import re
from subprocess import check_output
from subprocess import PIPE
from subprocess import Popen

import docker
import pkg_resources
import requests

from vent.api.templates import Template
from vent.helpers.logs import Logger
from vent.helpers.paths import PathDirs

logger = Logger(__name__)


def Version():
    """ Get Vent version """
    version = ''
    try:
        version = pkg_resources.require('vent')[0].version
        if not version.startswith('v'):
            version = 'v' + version
    except Exception as e:  # pragma: no cover
        version = 'Error: ' + str(e)
    return version


def System():
    """ Get system operating system """
    return platform.system()


def Docker():
    """ Get Docker setup information """
    docker_info = {'server': {}, 'env': '', 'type': '', 'os': ''}

    # get docker server version
    try:
        d_client = docker.from_env()
        docker_info['server'] = d_client.version()
    except Exception as e:  # pragma: no cover
        logger.error("Can't get docker info " + str(e))

    # get operating system
    system = System()
    docker_info['os'] = system

    # check if native or using docker-machine
    if 'DOCKER_MACHINE_NAME' in os.environ:
        # using docker-machine
        docker_info['env'] = os.environ['DOCKER_MACHINE_NAME']
        docker_info['type'] = 'docker-machine'
    elif 'DOCKER_HOST' in os.environ:
        # not native
        docker_info['env'] = os.environ['DOCKER_HOST']
        docker_info['type'] = 'remote'
    else:
        # using "local" server
        docker_info['type'] = 'native'
    return docker_info


def Containers(vent=True, running=True, exclude_labels=None):
    """
    Get containers that are created, by default limit to vent containers that
    are running
    """
    containers = []

    try:
        d_client = docker.from_env()
        if vent:
            c = d_client.containers.list(all=not running,
                                         filters={'label': 'vent'})
        else:
            c = d_client.containers.list(all=not running)
        for container in c:
            include = True
            if exclude_labels:
                for label in exclude_labels:
                    if 'vent.groups' in container.labels and label in container.labels['vent.groups']:
                        include = False
            if include:
                containers.append((container.name, container.status))
    except Exception as e:  # pragma: no cover
        logger.error('Docker problem ' + str(e))

    return containers


def Cpu():
    """ Get number of available CPUs """
    cpu = 'Unknown'

    try:
        cpu = str(multiprocessing.cpu_count())
    except Exception as e:  # pragma: no cover
        logger.error("Can't access CPU count' " + str(e))
    return cpu


def Gpu(pull=False):
    """ Check for support of GPUs, and return what's available """
    gpu = (False, '')

    try:
        image = 'nvidia/cuda:8.0-runtime'
        image_name, tag = image.split(':')
        d_client = docker.from_env()
        nvidia_image = d_client.images.list(name=image)

        if pull and len(nvidia_image) == 0:
            try:
                d_client.images.pull(image_name, tag=tag)
                nvidia_image = d_client.images.list(name=image)
            except Exception as e:  # pragma: no cover
                logger.error('Something with the GPU went wrong ' + str(e))

        if len(nvidia_image) > 0:
            cmd = 'nvidia-docker run --rm ' + image + ' nvidia-smi -L'
            proc = Popen([cmd],
                         stdout=PIPE,
                         stderr=PIPE,
                         shell=True,
                         close_fds=True)
            gpus = proc.stdout.read()
            err = proc.stderr.read()
            if gpus:
                gpu_str = ''
                for line in gpus.strip().split('\n'):
                    gpu_str += line.split(' (UUID: ')[0] + ', '
                gpu = (True, gpu_str[:-2])
            else:
                if err:
                    gpu = (False, 'Unknown', str(err))
                else:
                    gpu = (False, 'None')
        else:
            gpu = (False, 'None')
    except Exception as e:  # pragma: no cover
        gpu = (False, 'Unknown', str(e))
    return gpu


def GpuUsage(**kargs):
    """ Get the current GPU usage of available GPUs """
    usage = (False, None)
    gpu_status = {'vent_usage': {'dedicated': [], 'mem_mb': {}}}

    path_dirs = PathDirs(**kargs)
    path_dirs.host_config()
    template = Template(template=path_dirs.cfg_file)

    # get running jobs using gpus
    try:
        d_client = docker.from_env()
        c = d_client.containers.list(all=False,
                                     filters={'label': 'vent-plugin'})
        for container in c:
            if ('vent.gpu' in container.attrs['Config']['Labels'] and
                    container.attrs['Config']['Labels']['vent.gpu'] == 'yes'):
                device = container.attrs['Config']['Labels']['vent.gpu.device']
                if ('vent.gpu.dedicated' in container.attrs['Config']['Labels'] and
                        container.attrs['Config']['Labels']['vent.gpu.dedicated'] == 'yes'):
                    gpu_status['vent_usage']['dedicated'].append(device)
                elif 'vent.gpu.mem_mb' in container.attrs['Config']['Labels']:
                    if device not in gpu_status['vent_usage']['mem_mb']:
                        gpu_status['vent_usage']['mem_mb'][device] = 0
                    gpu_status['vent_usage']['mem_mb'][device] += int(
                        container.attrs['Config']['Labels']['vent.gpu.mem_mb'])
    except Exception as e:  # pragma: no cover
        logger.error('Could not get running jobs ' + str(e))

    port = '3476'
    # default docker gateway
    host = '172.17.0.1'
    result = template.option('nvidia-docker-plugin', 'port')
    if result[0]:
        port = result[1]
    result = template.option('nvidia-docker-plugin', 'host')
    if result[0]:
        host = result[1]
    else:
        try:
            # now just requires ip, ifconfig
            route = check_output(('ip', 'route')).decode('utf-8').split('\n')
            default = ''
            # grab the default network device.
            for device in route:
                if 'default' in device:
                    default = device.split()[4]
                    break

            # grab the IP address for the default device
            ip_addr = check_output(('ifconfig', default)).decode('utf-8')
            ip_addr = ip_addr.split('\n')[1].split()[1]
            host = ip_addr
        except Exception as e:  # pragma: no cover
            logger.error('Something with the ip addresses'
                         'went wrong ' + str(e))

    # have to get the info separately to determine how much memory is availabe
    nd_url = 'http://' + host + ':' + port + '/v1.0/gpu/info/json'
    try:
        r = requests.get(nd_url)
        if r.status_code == 200:
            status = r.json()
            for i, device in enumerate(status['Devices']):
                gm = int(round(math.log(int(device['Memory']['Global']), 2)))
                gpu_status[i] = {'global_memory': 2**gm,
                                 'cores': device['Cores']}
        else:
            usage = (False, 'Unable to get GPU usage request error code: ' +
                     str(r.status_code))
    except Exception as e:  # pragma: no cover
        usage = (False, 'Error: ' + str(e))

    # get actual status of each gpu
    nd_url = 'http://' + host + ':' + port + '/v1.0/gpu/status/json'
    try:
        r = requests.get(nd_url)
        if r.status_code == 200:
            status = r.json()
            for i, device in enumerate(status['Devices']):
                if i not in gpu_status:
                    gpu_status[i] = {}
                gpu_status[i]['utilization'] = device['Utilization']
                gpu_status[i]['memory'] = device['Memory']
                gpu_status[i]['processes'] = device['Processes']
            usage = (True, gpu_status)
        else:
            usage = (False, 'Unable to get GPU usage request error code: ' +
                     str(r.status_code))
    except Exception as e:  # pragma: no cover
        usage = (False, 'Error: ' + str(e))

    return usage


def Images(vent=True):
    """ Get images that are build, by default limit to vent images """
    images = []
    # TODO needs to also check images in the manifest that couldn't have the
    #      label added
    try:
        d_client = docker.from_env()
        if vent:
            i = d_client.images.list(filters={'label': 'vent'})
        else:
            i = d_client.images.list()
        for image in i:
            images.append((image.tags[0], image.short_id))
    except Exception as e:  # pragma: no cover
        logger.error('Something with the Images went wrong ' + str(e))

    return images


def Jobs():
    """
    Get the number of jobs that are running and finished, and the number of
    total tools running and finished for those jobs
    """
    jobs = [0, 0, 0, 0]

    # get running jobs
    try:
        d_client = docker.from_env()
        c = d_client.containers.list(all=False,
                                     filters={'label': 'vent-plugin'})
        files = []
        for container in c:
            jobs[1] += 1
            if 'file' in container.attrs['Config']['Labels']:
                if container.attrs['Config']['Labels']['file'] not in files:
                    files.append(container.attrs['Config']['Labels']['file'])
        jobs[0] = len(files)
    except Exception as e:  # pragma: no cover
        logger.error('Could not get running jobs ' + str(e))

    # get finished jobs
    try:
        d_client = docker.from_env()
        c = d_client.containers.list(all=True,
                                     filters={'label': 'vent-plugin',
                                              'status': 'exited'})

        file_names = []
        tool_names = []
        finished_jobs = []
        path_dirs = PathDirs()
        manifest = os.path.join(path_dirs.meta_dir, 'status.json')

        if os.path.exists(manifest):
            file_status = 'a'
        else:
            file_status = 'w'

        # get a list of past jobs' file names if status.json exists
        if file_status == 'a':
            with open(manifest, 'r') as infile:
                for line in infile:
                    finished_jobs.append(json.loads(line))

            # get a list of file names so we can check against each container
            file_names = [d['FileName'] for d in finished_jobs]

            # multiple tools can run on 1 file. Use a tuple to status check
            tool_names = [(d['FileName'], d['VentPlugin'])
                          for d in finished_jobs]

        for container in c:
            jobs[3] += 1

            if 'file' in container.attrs['Config']['Labels']:
                # make sure the file name and the tool tup exists because
                # multiple tools can run on 1 file.
                if (container.attrs['Config']['Labels']['file'],
                    container.attrs['Config']['Labels']['vent.name']) not in \
                        tool_names:
                    # TODO figure out a nicer way of getting desired values
                    # from containers.attrs.
                    new_file = {}
                    new_file['FileName'] = \
                        container.attrs['Config']['Labels']['file']
                    new_file['VentPlugin'] = \
                        container.attrs['Config']['Labels']['vent.name']
                    new_file['StartedAt'] = \
                        container.attrs['State']['StartedAt']
                    new_file['FinishedAt'] = \
                        container.attrs['State']['FinishedAt']
                    new_file['ID'] = \
                        container.attrs['Id'][:12]

                    # create/append a json file with all wanted information
                    with open(manifest, file_status) as outfile:
                        json.dump(new_file, outfile)
                        outfile.write('\n')

                # delete any containers with 'vent-plugin' in the groups
                if 'vent-plugin' in container.attrs['Config']['Labels']:
                    container.remove()

        # add extra one to account for file that just finished if the file was
        # just created since file_names is processed near the beginning
        if file_status == 'w' and len(file_names) == 1:
            jobs[2] = len(set(file_names)) + 1
        else:
            jobs[2] = len(set(file_names))

        jobs[3] = jobs[3] - jobs[1]

    except Exception as e:  # pragma: no cover
        logger.error('Could not get finished jobs ' + str(e))

    return tuple(jobs)


def Tools(**kargs):
    """ Get tools that exist in the manifest """
    path_dirs = PathDirs(**kargs)
    manifest = os.path.join(path_dirs.meta_dir, 'plugin_manifest.cfg')
    template = Template(template=manifest)
    tools = template.sections()
    return tools[1]


def Services(core, vent=True, external=False, **kargs):
    """
    Get services that have exposed ports, expects param core to be True or
    False based on which type of services to return, by default limit to vent
    containers and processes not running externally, if not limited by vent
    containers, then core is ignored.
    """
    services = []
    path_dirs = PathDirs(**kargs)
    template = Template(template=path_dirs.cfg_file)
    services_uri = template.option('main', 'services_uri')
    try:
        # look for internal services
        if not external:
            d_client = docker.from_env()
            if vent:
                c_filter = {'label': 'vent'}
                containers = d_client.containers.list(filters=c_filter)
            else:
                containers = d_client.containers.list()
            for c in containers:
                uris = {}
                name = None
                if vent and 'vent.name' in c.attrs['Config']['Labels']:
                    if ((core and
                         'vent.groups' in c.attrs['Config']['Labels'] and
                         'core' in c.attrs['Config']['Labels']['vent.groups']) or
                        (not core and
                         'vent.groups' in c.attrs['Config']['Labels'] and
                         'core' not in c.attrs['Config']['Labels']['vent.groups'])):
                        name = c.attrs['Config']['Labels']['vent.name']
                        if name == '':
                            name = c.attrs['Config']['Labels']['vent.namespace'].split(
                                '/')[1]
                        for label in c.attrs['Config']['Labels']:
                            if label.startswith('uri'):
                                try:
                                    val = int(label[-1])
                                    if val not in uris:
                                        uris[val] = {}
                                    uris[val][label[:-1]
                                              ] = c.attrs['Config']['Labels'][label]
                                except Exception as e:  # pragma: no cover
                                    logger.error('Malformed services section'
                                                 ' in the template file '
                                                 + str(e))
                else:
                    name = c.name
                if name and 'vent.repo' in c.attrs['Config']['Labels']:
                    name = c.attrs['Config']['Labels']['vent.repo'].split(
                        '/')[-1] + ': ' + name
                ports = c.attrs['NetworkSettings']['Ports']
                p = []
                port_num = 1
                for port in ports:
                    if ports[port]:
                        try:
                            service_str = ''
                            if 'uri_prefix' in uris[port_num]:
                                service_str += uris[port_num]['uri_prefix']
                            host = ports[port][0]['HostIp']
                            if services_uri[0] and host == '0.0.0.0':
                                host = services_uri[1]
                            service_str += host + ':'
                            service_str += ports[port][0]['HostPort']
                            if 'uri_postfix' in uris[port_num]:
                                service_str += uris[port_num]['uri_postfix']
                            uri_creds = ''
                            if 'uri_user' in uris[port_num]:
                                uri_creds += ' user:'
                                uri_creds += uris[port_num]['uri_user']
                            if 'uri_pw' in uris[port_num]:
                                uri_creds += ' pw:'
                                uri_creds += uris[port_num]['uri_pw']
                            if uri_creds:
                                service_str += ' - (' + uri_creds + ' )'
                            p.append(service_str)
                        except Exception as e:  # pragma: no cover
                            logger.info('No services defined for ' + str(name) + ' with exposed port ' +
                                        str(port_num) + ' because: ' + str(e))
                        port_num += 1
                if p and name:
                    services.append((name, p))
                    logger.info(services)
        # look for external services
        else:
            ext_tools = template.section('external-services')[1]
            for ext_tool in ext_tools:
                try:
                    name = ext_tool[0].lower()
                    p = []
                    settings_dict = json.loads(ext_tool[1])
                    if ('locally_active' in settings_dict and
                            settings_dict['locally_active'] == 'no'):
                        # default protocol to display will be http
                        protocol = 'http'
                        ip_address = ''
                        port = ''
                        for setting in settings_dict:
                            if setting == 'ip_address':
                                ip_address = settings_dict[setting]
                            if setting == 'port':
                                port = settings_dict[setting]
                            if setting == 'protocol':
                                protocol = settings_dict[setting]
                        p.append(protocol + '://' + ip_address + ':' + port)
                    if p and name:
                        services.append((name, p))
                except Exception:  # pragma: no cover
                    p = None
    except Exception as e:  # pragma: no cover
        logger.error('Could not get services ' + str(e))
    return services


def Timestamp():
    """ Get the current datetime in UTC """
    timestamp = ''
    try:
        timestamp = str(datetime.datetime.now())+' UTC'
    except Exception as e:  # pragma: no cover
        logger.error('Could not get current time ' + str(e))
    return timestamp


def Uptime():
    """ Get the current uptime information """
    uptime = ''
    try:
        uptime = check_output(['uptime'], close_fds=True).decode('utf-8')[1:]
    except Exception as e:  # pragma: no cover
        logger.error('Could not get current uptime ' + str(e))
    return uptime


def DropLocation():
    """ Get the directory that file drop is watching """
    template = Template(template=PathDirs().cfg_file)
    drop_loc = template.option('main', 'files')[1]
    drop_loc = os.path.expanduser(drop_loc)
    drop_loc = os.path.abspath(drop_loc)
    return (True, drop_loc)


def ParsedSections(file_val):
    """
    Get the sections and options of a file returned as a dictionary
    """
    try:
        template_dict = {}
        cur_section = ''
        for val in file_val.split('\n'):
            val = val.strip()
            if val != '':
                section_match = re.match(r'\[.+\]', val)
                if section_match:
                    cur_section = section_match.group()[1:-1]
                    template_dict[cur_section] = {}
                else:
                    option, value = val.split('=', 1)
                    option = option.strip()
                    value = value.strip()
                    if option.startswith('#'):
                        template_dict[cur_section][val] = ''
                    else:
                        template_dict[cur_section][option] = value
    except Exception:  # pragma: no cover
        template_dict = {}
    return template_dict


def Dependencies(tools):
    """
    Takes in a list of tools that are being updated and returns any tools that
    depend on linking to them
    """
    dependencies = []
    if tools:
        path_dirs = PathDirs()
        man = Template(os.path.join(path_dirs.meta_dir, 'plugin_manifest.cfg'))
        for section in man.sections()[1]:
            # don't worry about dealing with tool if it's not running
            running = man.option(section, 'running')
            if not running[0] or running[1] != 'yes':
                continue
            t_name = man.option(section, 'name')[1]
            t_branch = man.option(section, 'branch')[1]
            t_version = man.option(section, 'version')[1]
            t_identifier = {'name': t_name,
                            'branch': t_branch,
                            'version': t_version}
            options = man.options(section)[1]
            if 'docker' in options:
                d_settings = json.loads(man.option(section,
                                                   'docker')[1])
                if 'links' in d_settings:
                    for link in json.loads(d_settings['links']):
                        if link in tools:
                            dependencies.append(t_identifier)
    return dependencies
