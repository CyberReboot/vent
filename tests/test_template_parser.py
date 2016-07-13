import os
import pytest

from .. import template_parser

class PathDirs:
    """ Global path directories for parsing templates """
    def __init__(self,
                 base_dir=os.getcwd()+"/",
                 collectors_dir="collectors",
                 core_dir="core",
                 plugins_dir="plugins/",
                 plugin_repos="plugin_repos",
                 template_dir="templates/",
                 vis_dir="visualization"):
        self.base_dir = base_dir
        self.collectors_dir = base_dir + collectors_dir
        self.core_dir = base_dir + core_dir
        self.plugins_dir = base_dir + plugins_dir
        self.plugin_repos = base_dir + plugin_repos
        self.template_dir = base_dir + template_dir
        self.vis_dir = base_dir + vis_dir

def test_read_template_types():
    """ Testing reading from all templates """
    template_dir = "templates/"
    plugins_dir = "plugins/"

    os.system("cp core.backup templates/core.template")

    filedata = None
    with open(template_dir + 'core.template', 'r') as f:
        filedata = f.read()
    filedata = filedata.replace('#elasticsearch', 'elasticsearch')
    filedata = filedata.replace('#aaa-rabbitmq', 'aaa-rabbitmq')
    filedata = filedata.replace('#aaa-syslog', 'aaa-syslog')
    with open(template_dir + 'core.template', 'w') as f:
        f.write(filedata)

    template_parser.read_template_types("core", "", template_dir, plugins_dir)
    template_parser.read_template_types("active", "", template_dir, plugins_dir)
    template_parser.read_template_types("passive", "", template_dir, plugins_dir)
    template_parser.read_template_types("visualization", "", template_dir, plugins_dir)
    template_parser.read_template_types("all", "", template_dir, plugins_dir)
    template_parser.read_template_types("foo", "", template_dir, plugins_dir)

    os.system("cp modes.backup templates/modes.template")
    os.system('echo "core = all" >> templates/modes.template')
    template_parser.read_template_types("core", "", template_dir, plugins_dir)

    os.system("touch templates/foo.template")
    os.system("mkdir plugins/foo")
    os.system("mkdir plugins/foo/bar")
    os.system("mkdir plugins/foo/baz")
    template_parser.read_template_types("foo", "", template_dir, plugins_dir)
    os.system("cp modes.backup templates/modes.template")
    os.system('echo "foo = all" >> templates/modes.template')
    template_parser.read_template_types("foo", "", template_dir, plugins_dir)
    os.system('echo "[bar]" >> templates/foo.template')
    os.system('echo "HostConfig = {\"PublishAllPorts\": true}" >> templates/foo.template')
    template_parser.read_template_types("foo", "", template_dir, plugins_dir)
    os.system("cp modes.backup templates/modes.template")
    os.system('echo "foo = bar,baz" >> templates/modes.template')
    template_parser.read_template_types("foo", "foo", template_dir, plugins_dir)
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
    template_parser.read_template_types("zzz", "", template_dir, plugins_dir)
    os.system('echo "zzz = all" >> templates/modes.template')
    template_parser.read_template_types("zzz", "", template_dir, plugins_dir)
    os.system("cp modes.backup templates/modes.template")
    os.system('echo "zzz = bar,baz" >> templates/modes.template')
    template_parser.read_template_types("zzz", "", template_dir, plugins_dir)
    os.system("cp modes.backup templates/modes.template")

    # Negative Test Cases
    invalid_dir = "tmp/"
    template_parser.read_template_types("all", "", invalid_dir, plugins_dir)
    template_parser.read_template_types("plugs", "", template_dir, plugins_dir)
    template_parser.read_template_types("plugs", "", invalid_dir, plugins_dir)

    os.system("cp core.backup templates/core.template")

def test_execute_template():
    """ Testing executing template configurations """
    template_dir = "templates/"
    plugins_dir = "plugins/"

    info_name, service_schedule, tool_core, tool_dict, delay_sections = template_parser.read_template_types("core", "", template_dir, plugins_dir)
    template_parser.execute_template("core", "start", info_name, service_schedule, tool_core, tool_dict, delay_sections, template_dir, plugins_dir)
    template_parser.execute_template("invalid-template", "start", info_name, service_schedule, tool_core, tool_dict, delay_sections, template_dir, plugins_dir)
    template_parser.execute_template("invalid-template", [], info_name, "foo", tool_core, tool_dict, delay_sections, template_dir, plugins_dir)

def test_main():
    """ Testing main function """
    path_dirs = PathDirs()
    # Test starting all
    template_type = "all"
    template_execution = "start"
    container_cmd = ""
    template_parser.main(path_dirs, template_type, template_execution, container_cmd)
    # Test stopping all
    template_execution = "stop"
    template_parser.main(path_dirs, template_type, template_execution, container_cmd)
    # Test removing all
    template_execution = "clean"
    template_parser.main(path_dirs, template_type, template_execution, container_cmd)
    # Test starting cores
    template_type = "core"
    template_execution = "start"
    template_parser.main(path_dirs, template_type, template_execution, container_cmd)
    # Test stopping cores
    template_execution = "stop"
    template_parser.main(path_dirs, template_type, template_execution, container_cmd)
    # Test removing cores
    template_execution = "clean"
    template_parser.main(path_dirs, template_type, template_execution, container_cmd)


