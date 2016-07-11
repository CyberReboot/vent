import os
import pytest

from .. import template_parser

def test_read_template_types():
    """ Testing reading from all templates """
    template_dir = "templates/"
    plugins_dir = "plugins/"

    os.system("touch templates/test.template")
    os.system('echo "[bar]" >> templates/test.template')
    os.system('echo "HostConfig = {\"PublishAllPorts\": true}" >> templates/test.template')
    os.system("mkdir plugins/test")
    os.system("mkdir plugins/test/bar")
    os.system("mkdir plugins/test/baz")
    template_parser.read_template_types("test", "", template_dir, plugins_dir)
    os.system("cp templates/modes.template modes.backup")
    os.system('echo "test = all" >> templates/modes.template')
    template_parser.read_template_types("test", "", template_dir, plugins_dir)
    os.system("cp modes.backup templates/modes.template")
    os.system('echo "test = bar,baz" >> templates/modes.template')
    template_parser.read_template_types("test", "", template_dir, plugins_dir)
    os.system("cp modes.backup templates/modes.template")

    os.system("touch templates/foo.template")
    os.system('echo "[bar]" >> templates/foo.template')
    os.system('echo "HostConfig = {\"PublishAllPorts\": true, \"Links\": [\"core-aaa-rabbitmq:rabbitmq\"], \"Binds\":[\"/var/log/syslog-ng:/var/log/syslog-ng\"]}" >> templates/foo.template')
    os.system('echo "site_path = foo" >> templates/foo.template')
    os.system('echo "data_path = foo" >> templates/foo.template')
    os.system('echo "delay = 30" >> templates/foo.template')
    os.system('echo "" >> templates/foo.template')
    os.system('echo "[baz]" >> templates/foo.template')
    os.system('echo "HostConfig = {\"PublishAllPorts\": true}" >> templates/foo.template')
    os.system("mkdir plugins/foo")
    os.system("mkdir plugins/foo/bar")
    os.system("mkdir plugins/foo/baz")
    template_parser.read_template_types("foo", "", template_dir, plugins_dir)
    os.system('echo "foo = all" >> templates/modes.template')
    template_parser.read_template_types("foo", "", template_dir, plugins_dir)
    os.system("cp modes.backup templates/modes.template")
    os.system('echo "foo = bar,baz" >> templates/modes.template')
    template_parser.read_template_types("foo", "", template_dir, plugins_dir)
    os.system("cp modes.backup templates/modes.template")

    template_parser.read_template_types("core", "", template_dir, plugins_dir)
    template_parser.read_template_types("active", "", template_dir, plugins_dir)
    template_parser.read_template_types("passive", "", template_dir, plugins_dir)
    template_parser.read_template_types("visualization", "", template_dir, plugins_dir)
    template_parser.read_template_types("all", "", template_dir, plugins_dir)

    # Negative Test Cases
    invalid_dir = "tmp/"
    template_parser.read_template_types("all", "", invalid_dir, plugins_dir)
    template_parser.read_template_types("plugs", "", template_dir, plugins_dir)
    template_parser.read_template_types("plugs", "", invalid_dir, plugins_dir)

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
    template_parser.main()
