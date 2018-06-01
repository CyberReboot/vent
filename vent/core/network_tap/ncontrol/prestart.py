#!/usr/bin/env python3
import docker
d_client = docker.from_env()
d_client.images.pull('cyberreboot/vent-ncapture', tag='master')
