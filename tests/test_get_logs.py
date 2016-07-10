import os
import pytest
import sys

from vent.info_tools import get_logs

def test_msg():
    """ tests custom output """
    get_logs.msg()

def test_init():
    """ tests argparse initialization """
    get_logs.set_parser()

def test_no_args():
    """ tests get_logs with no arguments """
    parser = get_logs.set_parser()
    os.system('docker run --name core-aaa-syslog -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"')
    os.system('docker commit core-aaa-syslog core/aaa-syslog')
    get_logs.parse_args(parser.parse_args([]), parser)

def test_all_flag():
    """ tests get_logs using -a flag, and combinations that start with -a """
    parser = get_logs.set_parser()
    get_logs.parse_args(parser.parse_args(['-a']), parser)
    get_logs.parse_args(parser.parse_args(['-a', '-c', 'test']), parser)
    get_logs.parse_args(parser.parse_args(['-a', '-n']), parser)
    #invalid args
    get_logs.parse_args(parser.parse_args(['-a', '-f']), parser)

def test_container_flag():
    """ tests get_logs using -c flag, and combinations that start with -c """
    parser = get_logs.set_parser()
    get_logs.parse_args(parser.parse_args(['-c', 'example-container']), parser)
    get_logs.parse_args(parser.parse_args(['-c', 'core-aaa-syslog']), parser)
    get_logs.parse_args(parser.parse_args(['-c', 'example-container', '-f', 'example-file']), parser)

def test_namespace_flag():
    """ tests get_logs using -n flag, and combinations that start with -n """
    parser = get_logs.set_parser()
    get_logs.parse_args(parser.parse_args(['-n', 'example-namespace']), parser)
    get_logs.parse_args(parser.parse_args(['-n', 'core']), parser)
    get_logs.parse_args(parser.parse_args(['-n', 'example-namespace', '-f', 'example-file']), parser)
    #invalid args
    get_logs.parse_args(parser.parse_args(['-n']), parser)

def test_file_flag():
    """ tests get_logs using -f flag, and combinations that start with -f """
    parser = get_logs.set_parser()
    get_logs.parse_args(parser.parse_args(['-f', 'example-file']), parser)
    #invalid args
    get_logs.parse_args(parser.parse_args(['-f']), parser)

def test_main():
    """ tests the main function """
    get_logs.main(['get_logs.py'])
    tmp = sys.argv
    sys.argv = ['get_logs.py', '-a']
    get_logs.main(['get_logs.py', '-a'])
    sys.argv = tmp
