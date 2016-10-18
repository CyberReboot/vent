import os
import pytest

from vent import template_parser

class PathDirs:
    """ Global path directories for parsing templates """
    def __init__(self,
                 base_dir=os.getcwd()+"/",
                 collectors_dir="collectors",
                 core_dir="vent/core",
                 plugins_dir="vent/plugins/",
                 plugin_repos="plugin_repos",
                 template_dir="vent/templates/",
                 info_dir="scripts/info_tools/",
                 vis_dir="visualization"):
        self.base_dir = base_dir
        self.collectors_dir = base_dir + collectors_dir
        self.core_dir = base_dir + core_dir
        self.plugins_dir = base_dir + plugins_dir
        self.plugin_repos = base_dir + plugin_repos
        self.template_dir = base_dir + template_dir
        self.info_dir = base_dir + info_dir
        self.vis_dir = base_dir + vis_dir

def test_path_dirs():
    """testing PathDirs implementation in template_parser.py"""
    p_dirs = template_parser.PathDirs()

def test_read_template_types():
    """ Testing reading from all templates """
    path_dirs = PathDirs()

    os.system("cp core.backup templates/core.template")

    template_parser.read_template_types("core", "", path_dirs)
    template_parser.read_template_types("active", "", path_dirs)
    template_parser.read_template_types("passive", "", path_dirs)
    template_parser.read_template_types("visualization", "", path_dirs)
    template_parser.read_template_types("all", "", path_dirs)
    template_parser.read_template_types("foo", "", path_dirs)

    filedata = None
    with open(path_dirs.template_dir + 'core.template', 'r') as f:
        filedata = f.read()
    filedata = filedata.replace('#elasticsearch', 'elasticsearch')
    filedata = filedata.replace('#aaa-rabbitmq', 'aaa-rabbitmq')
    filedata = filedata.replace('#aaa-syslog', 'aaa-syslog')
    with open(path_dirs.template_dir + 'core.template', 'w') as f:
        f.write(filedata)

    template_parser.read_template_types("core", "", path_dirs)
    template_parser.read_template_types("active", "", path_dirs)
    template_parser.read_template_types("passive", "", path_dirs)
    template_parser.read_template_types("visualization", "", path_dirs)
    template_parser.read_template_types("all", "", path_dirs)
    template_parser.read_template_types("foo", "", path_dirs)

    filedata = None
    with open(path_dirs.template_dir + 'core.template', 'r') as f:
        filedata = f.read()
    filedata = filedata.replace('#rmq-es-connector', 'rmq-es-connector')
    filedata = filedata.replace('#passive = off', 'passive = on')
    filedata = filedata.replace('#active', 'active')
    with open(path_dirs.template_dir + 'core.template', 'w') as f:
        f.write(filedata)

    template_parser.read_template_types("core", "", path_dirs)
    template_parser.read_template_types("active", "", path_dirs)
    template_parser.read_template_types("passive", "", path_dirs)
    template_parser.read_template_types("visualization", "", path_dirs)
    template_parser.read_template_types("all", "", path_dirs)
    template_parser.read_template_types("foo", "", path_dirs)

    os.system("cp modes.backup templates/modes.template")
    os.system('echo "core = all" >> templates/modes.template')
    template_parser.read_template_types("core", "", path_dirs)

    os.system("touch templates/foo.template")
    os.system("mkdir plugins/foo")
    os.system("mkdir plugins/foo/bar")
    os.system("mkdir plugins/foo/baz")
    template_parser.read_template_types("foo", "", path_dirs)
    os.system("cp modes.backup templates/modes.template")
    os.system('echo "foo = all" >> templates/modes.template')
    template_parser.read_template_types("foo", "", path_dirs)
    os.system('echo "[bar]" >> templates/foo.template')
    os.system('echo "HostConfig = {\"PublishAllPorts\": true}" >> templates/foo.template')
    template_parser.read_template_types("foo", "", path_dirs)
    os.system("cp modes.backup templates/modes.template")
    os.system('echo "foo = bar,baz" >> templates/modes.template')
    template_parser.read_template_types("foo", "foo", path_dirs)
    os.system("cp modes.backup templates/modes.template")

    os.system("touch templates/zzz.template")
    os.system('echo "[bar]" >> templates/zzz.template')
    os.system('echo "HostConfig = {\"PublishAllPorts\": true, \"Links\": [\"core-aaa-rabbitmq:rabbitmq\"], \"Binds\":[\"/var/log/syslog-ng:/var/log/syslog-ng\"]}" >> templates/zzz.template')
    os.system('echo "site_path = foo" >> templates/zzz.template')
    os.system('echo "data_path = foo" >> templates/zzz.template')
    os.system('echo "delay = 30" >> templates/zzz.template')
    os.system('echo "" >> templates/zzz.template')
    os.system('echo "[baz]" >> templates/zzz.template')
    os.system('echo "data_path = foo" >> templates/zzz.template')
    os.system('echo "site_path = foo" >> templates/zzz.template')
    os.system("mkdir plugins/zzz")
    os.system("mkdir plugins/zzz/bar")
    os.system("mkdir plugins/zzz/baz")
    template_parser.read_template_types("zzz", "", path_dirs)
    os.system('echo "zzz = all" >> templates/modes.template')
    template_parser.read_template_types("zzz", "", path_dirs)
    os.system("cp modes.backup templates/modes.template")
    os.system('echo "zzz = bar,baz" >> templates/modes.template')
    template_parser.read_template_types("zzz", "", path_dirs)
    os.system("cp modes.backup templates/modes.template")

    # Negative Test Cases
    invalid_dirs = PathDirs()
    invalid_dirs.template_dir = "tmp/"
    template_parser.read_template_types("all", "", invalid_dirs)
    template_parser.read_template_types("plugs", "", path_dirs)
    template_parser.read_template_types("plugs", "", invalid_dirs)

    os.system("cp core.backup templates/core.template")

def test_execute_template():
    """ Testing executing template configurations """
    path_dirs = PathDirs()
    info_name, service_schedule, tool_core, tool_dict, delay_sections = template_parser.read_template_types("core", "", path_dirs)
    template_parser.execute_template("core", "start", info_name, service_schedule, tool_core, tool_dict, delay_sections)
    template_parser.execute_template("invalid-template", "start", info_name, service_schedule, tool_core, tool_dict, delay_sections)
    template_parser.execute_template("invalid-template", [], info_name, "foo", tool_core, tool_dict, delay_sections)

def test_main():
    """ Testing main function """
    path_dirs = PathDirs()
    # Stop running containers
    os.system("docker ps -q | xargs docker stop")
    for template_type in ["all", "core", "passive", "active", "visualization"]:
        # Test starting
        template_execution = "start"
        container_cmd = ""
        template_parser.main(path_dirs, template_type, template_execution, container_cmd)
        # Test stopping
        template_execution = "stop"
        template_parser.main(path_dirs, template_type, template_execution, container_cmd)
        # Test removing
        template_execution = "clean"
        template_parser.main(path_dirs, template_type, template_execution, container_cmd)
