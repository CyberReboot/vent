import os

from vent.api.actions import Action


def test_startup():
    """
    Test the startup function; uses the startup file configured in
    .setup_travis in order to populate the startup file with fields
    """
    instance = Action()
    status = instance.startup()
    assert isinstance(status, tuple)
    assert status[0]
    with open(instance.plugin.manifest, 'r') as man:
        assert 'rabbitmq' in man.read()


def test_add():
    """ Test the add function """
    instance = Action()
    status = instance.add('bad')
    assert isinstance(status, tuple)
    assert status[0] == False
    status = instance.add('https://github.com/cyberreboot/vent', build=False)
    assert isinstance(status, tuple)
    assert status[0] == True


def test_add_image():
    """ Test the add image function """
    instance = Action()
    status = instance.add_image('alpine', 'alpine')
    assert isinstance(status, tuple)
    assert status[0] == True


def test_get_configure():
    """ Test the get_configure function """
    instance = Action()
    status = instance.get_configure(name='elasticsearch')
    assert status[0]
    assert 'Elasticsearch' in status[1]


def test_save_configure():
    """ Test the save_configure function """
    instance = Action()
    status = instance.save_configure(name='elasticsearch',
                                     config_val='[info]\ntesting123 = testing123')
    assert isinstance(status, tuple)
    assert status[0]
    template_path = os.path.join(instance.p_helper.path_dirs.plugins_dir,
                                 'cyberreboot', 'vent', 'vent', 'core',
                                 'elasticsearch', 'vent.template')
    with open(template_path, 'r') as f:
        assert 'testing123' in f.read()
    with open(instance.p_helper.manifest, 'r') as man:
        assert 'testing123' in man.read()

    status = instance.save_configure(name='elasticsearch',
                                     config_val='[docker]\nrandom = instance',
                                     instances=2)
    assert isinstance(status, tuple)
    assert status[0]
    with open(instance.p_helper.manifest, 'r') as man:
        man_contents = man.read()
        assert 'random' in man_contents
        assert 'elasticsearch2' in man_contents


def test_remove():
    """ Test the remove function """
    instance = Action()
    status = instance.remove()
    assert isinstance(status, tuple)
    assert status[0] == True
    status = instance.remove(repo='https://github.com/cyberreboot/vent')
    assert isinstance(status, tuple)
    assert status[0] == True


def test_build():
    """ Test the build function """
    instance = Action()
    status = instance.add('https://github.com/cyberreboot/vent-plugins',
                          branch='master',
                          tools=[('kibana', '')],
                          build=False)
    assert isinstance(status, tuple)
    assert status[0] == True
    status = instance.build(branch='master', name='kibana')
    assert isinstance(status, tuple)
    assert status[0] == True


def test_prep_start():
    """ Test the prep_start function """
    instance = Action()
    status = instance.add('https://github.com/cyberreboot/vent-plugins',
                          branch='master',
                          tools=[('kibana', '')],
                          groups='foo')
    assert isinstance(status, tuple)
    assert status[0] == True
    status = instance.prep_start(name='kibana', branch='master')
    assert isinstance(status, tuple)
    assert status[0] == True
    status = instance.add('https://github.com/cyberreboot/vent',
                          branch='master',
                          tools=[('vent/core/file_drop', ''),
                                 ('vent/core/redis', ''),
                                 ('vent/core/syslog', '')])
    assert isinstance(status, tuple)
    assert status[0] == True
    status = instance.prep_start(groups='core', branch='master')
    assert isinstance(status, tuple)
    assert status[0] == True


def test_start():
    """ Test the start function """
    instance = Action()
    status = instance.start({})
    assert isinstance(status, tuple)
    assert status[0] == True


def test_disable():
    """ Test the disable function """
    instance = Action()
    status = instance.add('https://github.com/cyberreboot/vent',
                          branch='master',
                          tools=[('vent/core/elasticsearch', '')])
    assert isinstance(status, tuple)
    assert status[0]
    status = instance.disable(name='elasticsearch')
    assert isinstance(status, tuple)
    assert status[0]


def test_enable():
    """ Test the enable function """
    instance = Action()
    status = instance.add('https://github.com/cyberreboot/vent',
                          branch='master',
                          tools=[('vent/core/elasticsearch', '')])
    assert isinstance(status, tuple)
    assert status[0]
    status = instance.enable(name='elasticsearch')
    assert isinstance(status, tuple)
    assert status[0]


def test_update():
    """ Test the update function """
    instance = Action()
    status = instance.add('https://github.com/cyberreboot/vent',
                          branch='master',
                          tools=[('vent/core/elasticsearch', '')])
    assert isinstance(status, tuple)
    assert status[0]
    status = instance.update(name='elasticsearch', branch='master',
                             new_version='a45e8b3c79964c9a6953b6b45f079bd833edbf46')
    assert isinstance(status, tuple)
    assert status[0]


def test_restart_tools():
    instance = Action()
    status = instance.restart_tools(main_cfg=True, old_val='', new_val='')
    assert isinstance(status, tuple)
    assert status[0]
    status = instance.restart_tools(
        main_cfg=True, old_val='junk', new_val='[ext]')
    assert isinstance(status, tuple)
    assert status[0]
    status = instance.restart_tools()
    assert isinstance(status, tuple)
    assert status[0]


def test_stop():
    """ Test the stop function """
    instance = Action()
    status = instance.stop()
    assert isinstance(status, tuple)


def test_clean():
    """ Test the clean function """
    instance = Action()
    status = instance.clean()
    assert isinstance(status, tuple)
    status = instance.clean(name='rq_worker2')
    assert isinstance(status, tuple)


def test_backup():
    """ Test the backup function """
    vent_config = os.path.join(os.path.expanduser('~'), '.vent', 'vent.cfg')
    with open(vent_config, 'w') as f:
        f.write('[main]\nfiles = /test')
    instance = Action()
    status = instance.backup()
    assert isinstance(status, tuple)
    assert status[0] == True
    assert os.path.exists(status[1])


def test_restore():
    """ Test the restore function """
    instance = Action()
    status = instance.restore('not a backup')
    assert isinstance(status, tuple)
    assert status[0] == False


def test_inventory():
    """ Test the inventory function """
    instance = Action()
    status = instance.inventory(choices=[])
    assert isinstance(status, tuple)
    assert status[0] == False
    status = instance.inventory(choices=['repos',
                                         'core',
                                         'tools',
                                         'images',
                                         'built',
                                         'running',
                                         'enabled',
                                         'foo'])
    assert isinstance(status, tuple)
    assert status[0] == True
    assert isinstance(status[1], dict)


def test_configure():
    """ Test the configure function """
    Action.configure()


def test_upgrade():
    """ Test the upgrade function """
    Action.upgrade()


def test_reset():
    """ Test the reset function """
    instance = Action()
    status = instance.reset()
    assert isinstance(status, tuple)
    assert status[0]


def test_logs():
    """ Test the logs function """
    instance = Action()
    status = instance.logs()
    assert isinstance(status, tuple)
    assert status[0] == True
    status = instance.logs(grep_list=['foo'])
    assert isinstance(status, tuple)
    assert status[0] == True
    status = instance.logs(c_type='core')
    assert isinstance(status, tuple)
    assert status[0] == True


def test_tool_status_checker():
    """ Test the tool_status_checker function """
    instance = Action()
    status = instance.tool_status_checker('elasticsearch')


def test_tool_status_output():
    """ Test the tool_status_output function """
    instance = Action()
    status = instance.tool_status_output('elasticsearch')


def test_get_vent_tool_url():
    """ Test the get_vent_tool_url function """
    instance = Action()
    status = instance.get_vent_tool_url('elasticsearch')


def test_help():
    """ Test the help function """
    Action.help()
