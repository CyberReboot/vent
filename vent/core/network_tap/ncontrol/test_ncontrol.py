#!/usr/bin/python
import docker
import falcon
import pytest
from falcon import testing

from .ncontrol import api
from .prestart import pull_ncapture


@pytest.fixture
def client():
    return testing.TestClient(api)


def test_pull_ncapture():
    pull_ncapture()


def test_create_r(client):
    """ tests the restful endpoint: create """
    # test create
    payload = {'id': 'foo', 'interval': '60', 'filter': '', 'nic': 'eth1'}
    r = client.simulate_post('/create', json=payload)
    assert r.status == '200 OK'
    r = client.simulate_post('/create', json={'id': 'foo',
                                              'interval': '60',
                                              'iters': '1',
                                              'filter': '',
                                              'nic': 'eth1'})
    assert r.status == '200 OK'
    r = client.simulate_post('/create', json={})
    assert r.status == '200 OK'
    r = client.simulate_post('/create', json={'nic': 'eth1'})
    assert r.status == '200 OK'
    r = client.simulate_post('/create', json={'nic': 'eth1', 'id': 'foo'})
    assert r.status == '200 OK'
    r = client.simulate_post(
        '/create', json={'nic': 'eth1', 'id': 'foo', 'interval': '61'})
    assert r.status == '200 OK'
    r = client.simulate_post('/create', json={'id': 'foo',
                                              'interval': '60',
                                              'filter': '',
                                              'metadata': '{"foo": "bar"}',
                                              'iters': '1',
                                              'nic': 'eth1'})
    assert r.status == '200 OK'


def test_update_r(client):
    """ tests the restful endpoint: update """
    r = client.simulate_post('/update', json={'id': 'foo'})
    assert r.status == '200 OK'
    r = client.simulate_post('/update', json={'id': 'foo',
                                              'metadata': '{"foo": "bar"}'},
                             headers={'Content-Type': 'application/json'})
    assert r.status == '200 OK'


def test_info_r(client):
    """ tests the restful endpoint: info """
    # test info
    r = client.simulate_get('/info')
    assert r.status == '200 OK'


def test_list_r(client):
    """ tests the restful endpoint: list """
    # test list
    r = client.simulate_get('/list')
    assert r.status == '200 OK'


def test_nics_r(client):
    """ tests the restful endpoint: nics """
    # test nics
    r = client.simulate_get('/nics')
    assert r.status == '200 OK'


def test_stop_r(client):
    """ tests the restful endpoint: stop """
    # create some container and start it
    d = docker.from_env()
    d.images.pull('alpine')
    test_cont = d.containers.create('alpine')

    # test stop
    r = client.simulate_post('/stop', json={})
    assert r.status == '200 OK'
    r = client.simulate_post('/stop', json={'id': test_cont.attrs['Id']})
    assert r.status == '200 OK'
    r = client.simulate_post('/stop', json={'id': []})
    assert r.status == '200 OK'


def test_start_r(client):
    """ tests the restful endpoint: start """
    # create some container
    d = docker.from_env()
    d.images.pull('alpine')
    test_cont = d.containers.create('alpine')

    # test start
    r = client.simulate_post('/start', json={})
    assert r.status == '200 OK'
    r = client.simulate_post('/start', json={'id': test_cont.attrs['Id']})
    assert r.status == '200 OK'
    r = client.simulate_post('/start', json={'id': []})
    assert r.status == '200 OK'


def test_delete_r(client):
    """ tests the restful endpoint: delete """
    # create some container and start it
    d = docker.from_env()
    d.images.pull('alpine')
    test_cont = d.containers.create('alpine')

    # test delete
    r = client.simulate_post('/delete', json={})
    assert r.status == '200 OK'
    r = client.simulate_post('/delete', json={'id': test_cont.attrs['Id']})
    assert r.status == '200 OK'
    r = client.simulate_post('/delete', json={'id': []})
    assert r.status == '200 OK'
