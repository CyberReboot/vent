import os
import pytest
import sys

from scripts.info_tools import get_namespaces
from tests import test_env

def test_init():
    """ tests argparse initialization """
    get_namespaces.set_parser()

def test_no_args():
    """ tests get_namespaces with no arguments """
    parser = get_namespaces.set_parser()
    get_namespaces.parse_args(parser.parse_args([]), parser)

def test_mimetypes_flag():
    """ tests get_namespaces using -m flag """
    path_dirs = test_env.PathDirs()
    parser = get_namespaces.set_parser()
    get_namespaces.parse_args(parser.parse_args(['-m']), parser)
    get_namespaces.parse_args(parser.parse_args(['-m', '-t', path_dirs.template_dir]), parser)

def test_template_dir_flag():
    """ tests get_namespaces using -t flag """
    parser = get_namespaces.set_parser()
    with pytest.raises(SystemExit):
        get_namespaces.parse_args(parser.parse_args(['-t']), parser)

def test_help_flag():
    """ tests get_namespaces using -h flag """
    parser = get_namespaces.set_parser()
    with pytest.raises(SystemExit):
        get_namespaces.parse_args(parser.parse_args(['-h']), parser)

def test_invalid_flag():
    """ tests get_namespaces using invalid flag """
    parser = get_namespaces.set_parser()
    with pytest.raises(SystemExit):
        get_namespaces.parse_args(parser.parse_args(['-z']), parser)

def test_main():
    """ tests the main function """
    get_namespaces.main(['get_namespaces.py'])
    tmp = sys.argv
    sys.argv = ['get_namespaces.py', '-m']
    get_namespaces.main(['get_namespaces.py', '-m'])
    sys.argv = tmp

def test_entrypoint():
    """ test the entrypoint of get_namespaces """
    path_dirs = test_env.PathDirs()
    os.system("python2.7 "+path_dirs.info_dir+"get_namespaces.py -m -t "+path_dirs.template_dir)
