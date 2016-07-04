import pytest

from .. import template_parser

def test_read_template_types():
    template_dir = "templates/"
    plugins_dir = "plugins/"
    template_parser.read_template_types("core", "", template_dir, plugins_dir)
    template_parser.read_template_types("active", "", template_dir, plugins_dir)
    template_parser.read_template_types("passive", "", template_dir, plugins_dir)
    template_parser.read_template_types("visualization", "", template_dir, plugins_dir)
    template_parser.read_template_types("all", "", template_dir, plugins_dir)

def test_execute_template():
    template_dir = "templates/"
    plugins_dir = "plugins/"
    info_name, service_schedule, tool_core, tool_dict, delay_sections = template_parser.read_template_types("core", "", template_dir, plugins_dir)
    template_parser.execute_template("core", "start", info_name, service_schedule, tool_core, tool_dict, delay_sections, template_dir, plugins_dir)
