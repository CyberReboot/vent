#!/usr/bin/python
import docker
import ncontrol
import web

from paste.fixture import TestApp


def start_web_app():
    """ starts the web app in a TestApp for testing """
    nf_inst = ncontrol.NControl()
    urls = nf_inst.urls()
    app = web.application(urls, globals())
    test_app = TestApp(app.wsgifunc())
    return test_app


def test_create_r():
    """ tests the restful endpoint: create """
    # get web app
    test_app = start_web_app()

    # test create
    r = test_app.post('/create', params={'id': 'foo',
                                         'interval': '60',
                                         'filter': '',
                                         'nic': 'eth1'},
                      headers={'Content-Type': 'application/json'})
    assert r.status == 200
    r = test_app.post('/create', params={'id': 'foo',
                                         'interval': '60',
                                         'iters': '1',
                                         'filter': '',
                                         'nic': 'eth1'},
                      headers={'Content-Type': 'application/json'})
    assert r.status == 200
    r = test_app.post('/create', params={})
    assert r.status == 200
    r = test_app.post('/create', params={'nic': 'eth1'})
    assert r.status == 200
    r = test_app.post('/create', params={'nic': 'eth1', 'id': 'foo'})
    assert r.status == 200
    r = test_app.post(
        '/create', params={'nic': 'eth1', 'id': 'foo', 'interval': '61'})
    assert r.status == 200
    r = test_app.post('/create', params='{}')
    assert r.status == 200
    r = test_app.post('/create', params={'id': 'foo',
                                         'interval': '60',
                                         'filter': '',
                                         'metadata': '{"foo": "bar"}',
                                         'iters': '1',
                                         'nic': 'eth1'},
                      headers={'Content-Type': 'application/json'})
    assert r.status == 200


def test_list_r():
    """ tests the restful endpoint: list """
    # get web app
    test_app = start_web_app()

    # test list
    r = test_app.get('/list')
    assert r.status == 200


def test_stop_r():
    """ tests the restful endpoint: stop """
    # get web app
    test_app = start_web_app()

    # create some container and start it
    d = docker.from_env()
    d.images.pull('alpine')
    test_cont = d.containers.create('alpine')

    # test stop
    r = test_app.post('/stop', params={})
    assert r.status == 200
    r = test_app.post('/stop', params={'id': test_cont.attrs['Id']})
    assert r.status == 200
    r = test_app.post('/stop', params={'id': []})
    assert r.status == 200


def test_start_r():
    """ tests the restful endpoint: start """
    # get web app
    test_app = start_web_app()

    # create some container
    d = docker.from_env()
    d.images.pull('alpine')
    test_cont = d.containers.create('alpine')

    # test start
    r = test_app.post('/start', params={})
    assert r.status == 200
    r = test_app.post('/start', params={'id': test_cont.attrs['Id']})
    assert r.status == 200
    r = test_app.post('/start', params={'id': []})
    assert r.status == 200


def test_delete_r():
    """ tests the restful endpoint: delete """
    # get web app
    test_app = start_web_app()

    # create some container and start it
    d = docker.from_env()
    d.images.pull('alpine')
    test_cont = d.containers.create('alpine')

    # test delete
    r = test_app.post('/delete', params={})
    assert r.status == 200
    r = test_app.post('/delete', params={'id': test_cont.attrs['Id']})
    assert r.status == 200
    r = test_app.post('/delete', params={'id': []})
    assert r.status == 200
