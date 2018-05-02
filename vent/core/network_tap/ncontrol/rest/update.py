import ast
import docker
import redis
import socket
import urlparse
import web


class UpdateR:
    """
    This endpoint is for updating a filter
    """

    @staticmethod
    def POST():
        """
        Send a POST request with id and metadata and it will update the
        existing filter metadata with those specifications
        """
        web.header('Content-Type', 'application/json')

        # verify payload is in the correct format
        data = web.data()
        try:
            payload = ast.literal_eval(data)
        except Exception as e:  # pragma: no cover
            # check if url encoded
            data_dict = urlparse.parse_qs(data)
            for key in data_dict:
                payload[key] = data_dict[key][0]

        # payload should have the following fields:
        # - id
        # - metadata

        # verify payload has necessary information
        if 'id' not in payload:
            return 'payload missing id'
        if 'metadata' not in payload:
            return 'payload missing metadata'

        # connect to redis
        r = None
        try:
            r = redis.StrictRedis(host='redis', port=6379, db=0)
        except Exception as e:  # pragma: no cover
            try:
                r = redis.StrictRedis(host='localhost', port=6379, db=0)
            except Exception as e:  # pragma: no cover
                return (False, 'unable to connect to redis because: ' + str(e))
        if r:
            metadata = {}
            try:
                metadata = ast.literal_eval(payload['metadata'])
            except Exception as e:  # pragma: no cover
                return (False, 'unable to convert metadata [ ' +
                        str(payload['metadata']) + ' ] into a dict because: ' +
                        str(e))
            try:
                r.hmset(payload['id'], metadata)
                r.hmset(metadata['endpoint_data']['ip-address'], {'poseidon_hash': payload['id']})
                r.sadd('ip_addresses', metadata['endpoint_data']['ip-address'])
            except Exception as e:  # pragma: no cover
                return (False,
                        'unable to store contents of the payload [ ' +
                        str(metadata) + ' ] in redis because: ' +
                        str(e))

        return (True, 'successfully updated filter ' + str(payload['id']))
