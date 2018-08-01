import docker
import falcon
from falcon_cors import CORS

from .routes import routes


cors = CORS(allow_all_origins=True)
api = application = falcon.API(middleware=[cors.middleware])

r = routes()
for route in r:
    api.add_route(route, r[route])

d_client = docker.from_env()
d_client.images.pull('cyberreboot/vent-ncapture', tag='master')
