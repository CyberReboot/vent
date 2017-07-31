#!/usr/bin/env python
import docker
import logging
import sys
import web

from rest.create import CreateR
from rest.delete import DeleteR
from rest.filters import FiltersR
from rest.nlist import ListR
from rest.start import StartR
from rest.stop import StopR


module_logger = logging.getLogger(__name__)


class NControlServer(object):
    """
    This class is responsible for initializing the urls and web server.
    """
    # need __new__ for tests, but fails to call __init__ when actually running
    def __new__(*args, **kw):
        if hasattr(sys, '_called_from_test'):
            module_logger.info("don't call __init__")
        else:  # pragma: no cover
            return object.__new__(*args, **kw)

    def __init__(self, port=8080, host='0.0.0.0'):  # pragma: no cover
        d_client = docker.from_env()
        d_client.images.pull('cyberreboot/vent-ncapture', tag='master')
        nf_inst = NControl()
        urls = nf_inst.urls()
        app = web.application(urls, globals())
        web.httpserver.runsimple(app.wsgifunc(), (host, port))


class NControl:
    """
    This class is for defining things needed to start up.
    """

    @staticmethod
    def urls():
        urls = (
            '/create', CreateR,
            '/filters', FiltersR,
            '/start/(.+)', StartR,
            '/stop/(.+)', StopR,
            '/list/(.+)', ListR,
            '/delete/(.+)', DeleteR
        )
        return urls

if __name__ == '__main__':
    NControlServer().app.run()
