#!/usr/bin/python
import falcon
from falcon import testing
import pytest

from .workflow import api


@pytest.fixture
def client():
    return testing.TestClient(api)


def test_data_r(client):
    """ tests the restful endpoint: data.json """
    # test data
    r = client.simulate_get('/data.json',
                            headers={'Content-Type': 'application/json'})
    assert r.status == '200 OK'
