import os
import pytest

def test_rq_dash_settings():
    os.environ['DASH_PREFIX'] = "test"
    os.environ['REMOTE_REDIS_HOST'] = "test"
    os.environ['REMOTE_REDIS_PORT'] = "test"
    os.environ['REMOTE_REDIS_PSWD'] = "test"
    import rq_dash_settings
