import os
import pytest

from vent.info_tools import get_logs

def test_msg():
	get_logs.msg()

def test_init():
	get_logs.set_parser()

def test_no_args():
	parser = get_logs.set_parser()
	get_logs.parse_args(parser.parse_args([]), parser)

def test_all_flag():
	parser = get_logs.set_parser()
	get_logs.parse_args(parser.parse_args(['-a']), parser)
	get_logs.parse_args(parser.parse_args(['-a', '-c', 'test']), parser)
	get_logs.parse_args(parser.parse_args(['-a', '-n']), parser)
	#invalid args
	get_logs.parse_args(parser.parse_args(['-a', '-f']), parser)

def test_container_flag():
	parser = get_logs.set_parser()
	get_logs.parse_args(parser.parse_args(['-c', 'example-container']), parser)
	get_logs.parse_args(parser.parse_args(['-c', 'example-container', '-f', 'example-file']), parser)

def test_namespace_flag():
	parser = get_logs.set_parser()
	get_logs.parse_args(parser.parse_args(['-n', 'example-namespace']), parser)
	get_logs.parse_args(parser.parse_args(['-n', 'example-namespace', '-f', 'example-file']), parser)
	#invalid args
	get_logs.parse_args(parser.parse_args(['-n']), parser)

def test_file_flag():
	parser = get_logs.set_parser()
	get_logs.parse_args(parser.parse_args(['-f', 'example-file']), parser)
	#invalid args
	get_logs.parse_args(parser.parse_args(['-f']), parser)