import datetime
import docker
import multiprocessing
import os
import pkg_resources
import platform
import subprocess

from vent.api.plugins import Plugin
from vent.api.templates import Template
from vent.helpers.paths import PathDirs

def Version():
    """ Get Vent version """
    version = ''
    try:
        version = "v"+pkg_resources.require("vent")[0].version
    except Exception as e: # pragma: no cover
        pass
    return version

def System():
    """ Get system operating system """
    return platform.system()

def Docker():
    """ Get Docker setup information """
    docker_info = {'server':{}, 'env':'', 'type':'', 'os':''}

    # get docker server version
    try:
        d_client = docker.from_env()
        docker_info['server'] = d_client.version()
    except Exception as e: # pragma: no cover
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
            c = d_client.containers.list(all=not running, filters={'label':'vent'})
        else:
            c = d_client.containers.list(all=not running)
        for container in c:
            containers.append((container.name, container.status))
    except Exception as e: # pragma: no cover
        pass

    return containers

def Cpu():
    cpu = "Unknown"
    try:
        cpu = str(multiprocessing.cpu_count())
    except Exception as e: # pragma: no cover
        pass
    return cpu

def Gpu():
    gpu = ""
    try:
        d_client = docker.from_env()
        nvidia_image = d_client.images.list(name='nvidia/cuda:8.0-runtime')
        if len(nvidia_image) > 0:
            proc = subprocess.Popen(['nvidia-docker run --rm nvidia/cuda:8.0-runtime nvidia-smi -L'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, close_fds=True)
            gpus = proc.stdout.read()
            if gpus:
                for line in gpus.strip().split("\n"):
                    gpu += line.split(" (UUID: ")[0] + ", "
                gpu = gpu[:-2]
            else:
                gpu = "None"
        else:
            gpu = "None"
    except Exception as e: # pragma: no cover
        gpu = "Unknown"
    return gpu

def Images(vent=True):
    """ Get images that are build, by default limit to vent images """
    images = []

    try:
        d_client = docker.from_env()
        if vent:
            i = d_client.images.list(filters={'label':'vent'})
        else:
            i = d_client.images.list()
        for image in i:
            images.append((image.tags[0], image.short_id))
    except Exception as e: # pragma: no cover
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
        c = d_client.containers.list(all=False, filters={'label':'vent-plugin'})
        files = []
        for container in c:
            jobs[1] += 1
            if 'file' in container.attrs['Config']['Labels']:
                if container.attrs['Config']['Labels']['file'] not in files:
                    files.append(container.attrs['Config']['Labels']['file'])
        jobs[0] = len(files)
    except Exception as e: #pragma: no cover
        pass

    # get finished jobs
    try:
        d_client = docker.from_env()
        c = d_client.containers.list(all=True, filters={'label':'vent-plugin'})
        files = []
        for container in c:
            jobs[3] += 1
            if 'file' in container.attrs['Config']['Labels']:
                if container.attrs['Config']['Labels']['file'] not in files:
                    files.append(container.attrs['Config']['Labels']['file'])
        jobs[2] = len(files)-jobs[0]
        jobs[3] = jobs[3]-jobs[1]
    except Exception as e: #pragma: no cover
        pass

    return tuple(jobs)

def Tools(**kargs):
    """ Get tools that exist in the manifest """
    path_dirs = PathDirs(**kargs)
    manifest = os.path.join(path_dirs.meta_dir, "plugin_manifest.cfg")
    template = Template(template=manifest)
    tools = template.sections()
    return tools[1]

def Services(vent=True):
    """
    Get services that have exposed ports, by default limit to vent containers
    """
    services = []
    try:
        d_client = docker.from_env()
        if vent:
            containers = d_client.containers.list(filters={'label':'vent'})
        else:
            containers = d_client.containers.list()
        for container in containers:
            if vent:
                name = container.attrs['Config']['Labels']['vent.name']
            else:
                name = container.name
            ports = container.attrs['NetworkSettings']['Ports']
            p = []
            for port in ports:
                if ports[port]:
                    p.append(ports[port][0]['HostIp']+":"+ports[port][0]['HostPort'])
            if p:
                services.append((name, p))
    except Exception as e: # pragma: no cover
        pass
    return services

def Core(branch="master", **kargs):
    """
    Get the normal core tools, and the currently installed/built/running ones,
    including custom core services
    """
    # !! TODO this might need to store namespaces/branches/versions
    core = {'built':[], 'running':[], 'installed':[], 'normal':[]}

    # get normal core tools
    plugins = Plugin(plugins_dir=".internals/plugins")
    status, cwd = plugins.clone('https://github.com/cyberreboot/vent')
    if status == 0:
        plugins.version = 'HEAD'
        plugins.branch = branch
        response = plugins.checkout()
        matches = plugins._available_tools(groups='core')
        for match in matches:
            core['normal'].append(match[0].split('/')[-1])
    else:
        core['normal'] = 'failed'

    # get core tools that have been installed
    path_dirs = PathDirs(**kargs)
    manifest = os.path.join(path_dirs.meta_dir, "plugin_manifest.cfg")
    template = Template(template=manifest)
    tools = template.sections()
    if tools[0]:
        for tool in tools[1]:
            groups = template.option(tool, "groups")
            if groups[0] and "core" in groups[1]:
                name = template.option(tool, "name")
                if name[0]:
                    core['installed'].append(name[1])

    # get core tools that have been built and/or are running
    try:
        d_client = docker.from_env()
        images = d_client.images.list()
        for image in images:
            try:
                if "vent.groups" in image.attrs['Labels'] and 'core' in image.attrs['Labels']['vent.groups']:
                    if 'vent.name' in image.attrs['Labels']:
                        core['built'].append(image.attrs['Labels']['vent.name'])
            except Exception as err: # pragma: no cover
                pass
        containers = d_client.containers.list()
        for container in containers:
            try:
                if "vent.groups" in container.attrs['Config']['Labels'] and 'core' in container.attrs['Config']['Labels']['vent.groups']:
                    if 'vent.name' in container.attrs['Config']['Labels']:
                        core['running'].append(container.attrs['Config']['Labels']['vent.name'])
            except Exception as err: # pragma: no cover
                pass
    except Exception as e: # pragma: no cover
        pass
    return core

def Timestamp():
    """ Get the current datetime in UTC """
    timestamp = ""
    try:
        timestamp = str(datetime.datetime.now())+" UTC"
    except Exception as e:
        pass
    return timestamp

def Uptime():
    """ Get the current uptime information """
    uptime = ""
    try:
        uptime = str(subprocess.check_output(["uptime"], close_fds=True))[1:]
    except Exception as e:
        pass
    return uptime
