import pytest

from .. import template_parser

def test_read_template_types():
    template_parser.read_template_types("core", "")
