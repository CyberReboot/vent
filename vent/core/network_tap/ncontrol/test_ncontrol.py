#!/usr/bin/python
import docker
import falcon
from falcon import testing
import pytest

from .ncontrol import api


@pytest.fixture
def client():
    return testing.TestClient(api)


def test_create_r(client):
    """ tests the restful endpoint: create """
    # test create
    r = client.simulate_post('/create', params={'id': 'foo',
                                         'interval': '60',
                                         'filter': '',
                                         'nic': 'eth1'},
                      headers={'Content-Type': 'application/json'})
    assert r.status == '200 OK'
    r = client.simulate_post('/create', params={'id': 'foo',
                                         'interval': '60',
                                         'iters': '1',
                                         'filter': '',
                                         'nic': 'eth1'},
                      headers={'Content-Type': 'application/json'})
    assert r.status == '200 OK'
    r = client.simulate_post('/create', params={})
    assert r.status == '200 OK'
    r = client.simulate_post('/create', params={'nic': 'eth1'})
    assert r.status == '200 OK'
    r = client.simulate_post('/create', params={'nic': 'eth1', 'id': 'foo'})
    assert r.status == '200 OK'
    r = client.simulate_post(
        '/create', params={'nic': 'eth1', 'id': 'foo', 'interval': '61'})
    assert r.status == '200 OK'
    r = client.simulate_post('/create', params={'id': 'foo',
                                         'interval': '60',
                                         'filter': '',
                                         'metadata': '{"foo": "bar"}',
                                         'iters': '1',
                                         'nic': 'eth1'},
                      headers={'Content-Type': 'application/json'})
    assert r.status == '200 OK'


def test_update_r(client):
    """ tests the restful endpoint: update """
    r = client.simulate_post('/update', params={'id': 'foo'})
    assert r.status == '200 OK'
    r = client.simulate_post('/update', params={'id': 'foo',
                                         'metadata': '{"foo": "bar"}'},
                      headers={'Content-Type': 'application/json'})
    assert r.status == '200 OK'


def test_list_r(client):
    """ tests the restful endpoint: list """
    # test list
    r = client.simulate_get('/list')
    assert r.status == '200 OK'


def test_stop_r(client):
    """ tests the restful endpoint: stop """
    # create some container and start it
    d = docker.from_env()
    d.images.pull('alpine')
    test_cont = d.containers.create('alpine')

    # test stop
    r = client.simulate_post('/stop', params={})
    assert r.status == '200 OK'
    r = client.simulate_post('/stop', params={'id': test_cont.attrs['Id']})
    assert r.status == '200 OK'
    r = client.simulate_post('/stop', params={'id': []})
    assert r.status == '200 OK'


def test_start_r(client):
    """ tests the restful endpoint: start """
    # create some container
    d = docker.from_env()
    d.images.pull('alpine')
    test_cont = d.containers.create('alpine')

    # test start
    r = client.simulate_post('/start', params={})
    assert r.status == '200 OK'
    r = client.simulate_post('/start', params={'id': test_cont.attrs['Id']})
    assert r.status == '200 OK'
    r = client.simulate_post('/start', params={'id': []})
    assert r.status == '200 OK'


def test_delete_r(client):
    """ tests the restful endpoint: delete """
    # create some container and start it
    d = docker.from_env()
    d.images.pull('alpine')
    test_cont = d.containers.create('alpine')

    # test delete
    r = client.simulate_post('/delete', params={})
    assert r.status == '200 OK'
    r = client.simulate_post('/delete', params={'id': test_cont.attrs['Id']})
    assert r.status == '200 OK'
    r = client.simulate_post('/delete', params={'id': []})
    assert r.status == '200 OK'
