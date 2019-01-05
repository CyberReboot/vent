#!/usr/bin/env python3
import docker


def pull_ncapture():
    d_client = docker.from_env()
    d_client.images.pull('cyberreboot/vent-ncapture', tag='master')


if __name__ == '__main__':  # pragma: no cover
    pull_ncapture()
