import datetime
import docker
import multiprocessing
import os
import pkg_resources
import platform
import subprocess

from vent.api.templates import Template
from vent.helpers.paths import PathDirs


def Version():
    """ Get Vent version """
    version = ''
    try:
        version = pkg_resources.require("vent")[0].version
        if not version.startswith('v'):
            version = 'v' + version
    except Exception as e:  # pragma: no cover
        pass
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
        pass

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


def Containers(vent=True, running=True):
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
            containers.append((container.name, container.status))
    except Exception as e:  # pragma: no cover
        pass

    return containers


def Cpu():
    """ Get number of available CPUs """
    cpu = "Unknown"
    try:
        cpu = str(multiprocessing.cpu_count())
    except Exception as e:  # pragma: no cover
        pass
    return cpu


def Gpu(pull=False):
    """ Check for support of GPUs, and return what's available """
    gpu = (False, "")
    try:
        image = 'nvidia/cuda:8.0-runtime'
        image_name, tag = image.split(":")
        d_client = docker.from_env()
        nvidia_image = d_client.images.list(name=image)

        if pull and len(nvidia_image) == 0:
            try:
                d_client.images.pull(image_name, tag=tag)
                nvidia_image = d_client.images.list(name=image)
            except Exception as e:  # pragma: no cover
                pass

        if len(nvidia_image) > 0:
            cmd = 'nvidia-docker run --rm ' + image + ' nvidia-smi -L'
            proc = subprocess.Popen([cmd],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    shell=True,
                                    close_fds=True)
            gpus = proc.stdout.read()
            err = proc.stderr.read()
            if gpus:
                gpu_str = ""
                for line in gpus.strip().split("\n"):
                    gpu_str += line.split(" (UUID: ")[0] + ", "
                gpu = (True, gpu_str[:-2])
            else:
                if err:
                    gpu = (False, "Unknown", str(err))
                else:
                    gpu = (False, "None")
        else:
            gpu = (False, "None")
    except Exception as e:  # pragma: no cover
        gpu = (False, "Unknown", str(e))
    return gpu


def GpuUsage():
    """ Get the current GPU usage of available GPUs """
    # TODO
    usage = ""
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
        pass

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
        pass

    # get finished jobs
    try:
        d_client = docker.from_env()
        c = d_client.containers.list(all=True,
                                     filters={'label': 'vent-plugin'})
        files = []
        for container in c:
            jobs[3] += 1
            if 'file' in container.attrs['Config']['Labels']:
                if container.attrs['Config']['Labels']['file'] not in files:
                    files.append(container.attrs['Config']['Labels']['file'])
        jobs[2] = len(files) - jobs[0]
        jobs[3] = jobs[3] - jobs[1]
    except Exception as e:  # pragma: no cover
        pass

    return tuple(jobs)


def Tools(**kargs):
    """ Get tools that exist in the manifest """
    path_dirs = PathDirs(**kargs)
    manifest = os.path.join(path_dirs.meta_dir, "plugin_manifest.cfg")
    template = Template(template=manifest)
    tools = template.sections()
    return tools[1]


def Services(core, vent=True):
    """
    Get services that have exposed ports, expects param core to be True or
    False based on which type of services to return, by default limit to vent
    containers, if not limited by vent containers, then core is ignored.
    """
    services = []
    try:
        d_client = docker.from_env()
        if vent:
            containers = d_client.containers.list(filters={'label': 'vent'})
        else:
            containers = d_client.containers.list()
        for c in containers:
            uri_prefix = ''
            uri_postfix = ''
            uri_user = ''
            uri_pw = ''
            name = None
            if vent and 'vent.name' in c.attrs['Config']['Labels']:
                if ((core and
                     'vent.groups' in c.attrs['Config']['Labels'] and
                     'core' in c.attrs['Config']['Labels']['vent.groups']) or
                    (not core and
                     'vent.groups' in c.attrs['Config']['Labels'] and
                     'core' not in c.attrs['Config']['Labels']['vent.groups'])):
                    name = c.attrs['Config']['Labels']['vent.name']
                    if 'uri_prefix' in c.attrs['Config']['Labels']:
                        uri_prefix = c.attrs['Config']['Labels']['uri_prefix']
                    if 'uri_postfix' in c.attrs['Config']['Labels']:
                        uri_postfix = c.attrs['Config']['Labels']['uri_postfix']
                    if 'uri_user' in c.attrs['Config']['Labels']:
                        uri_user = " user:"
                        uri_user += c.attrs['Config']['Labels']['uri_user']
                    if 'uri_pw' in c.attrs['Config']['Labels']:
                        uri_pw = " pw:"
                        uri_pw += c.attrs['Config']['Labels']['uri_pw']
            else:
                name = c.name
            ports = c.attrs['NetworkSettings']['Ports']
            p = []
            for port in ports:
                if ports[port]:
                    uri_creds = ''
                    if uri_user or uri_pw:
                        uri_creds = " - (" + uri_user + uri_pw + " )"
                    p.append(uri_prefix + ports[port][0]['HostIp'] + ":" +
                             ports[port][0]['HostPort'] + uri_postfix +
                             uri_creds)
            if p and name:
                services.append((name, p))
    except Exception as e:  # pragma: no cover
        pass
    return services


def Timestamp():
    """ Get the current datetime in UTC """
    timestamp = ""
    try:
        timestamp = str(datetime.datetime.now())+" UTC"
    except Exception as e:  # pragma: no cover
        pass
    return timestamp


def Uptime():
    """ Get the current uptime information """
    uptime = ""
    try:
        uptime = str(subprocess.check_output(["uptime"], close_fds=True))[1:]
    except Exception as e:  # pragma: no cover
        pass
    return uptime
