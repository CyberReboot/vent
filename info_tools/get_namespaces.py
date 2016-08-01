#!/usr/bin/env python2.7

import argparse
import ConfigParser
import os
import sys

def set_parser():
    """ initialize parser """
    parser = argparse.ArgumentParser(prog="get_namespaces")
    #parser.add_argument("-a", "--all",
    #                    help="print all of the namespaces installed",
    #                    action="store_true")
    parser.add_argument("-t", "--template_dir",
                        help="set template directory to get templates from",
                        default="/var/lib/docker/data/templates/", type=str)
    parser.add_argument("-m", "--mimetypes",
                        help="print all of the mimetypes supported by the installed namespaces",
                        action="store_true")
    return parser

def parse_args(args, parser):
    """ parse arguments, and output based on arguments passed in """
    if args.mimetypes:
        m_types = {}
        # !! TODO check installed namespaces based on images built, also check modes
        # check templates
        try:
            for f in os.listdir(args.template_dir):
                if f.endswith(".template") and f not in ["modes.template", "core.template"]:
                    try:
                        # get list of sections per template file
                        with open(args.template_dir+f): pass
                        config = ConfigParser.RawConfigParser()
                        # needed to preserve case sensitive options
                        config.optionxform=str
                        config.read(args.template_dir+f)
                        if config.has_section("service") and config.has_option("service", "mime_types"):
                            m_types[f.split(".template", -1)[0]] = config.get("service", "mime_types").split(",")
                        else:
                            m_types[f.split(".template", -1)[0]] = ["all"]
                        sections = config.sections()
                    except Exception as e:
                        pass
        except Exception as e:
            pass
        print(str(m_types))
    else:
        parser.print_help()
    return

def main(args):
    """ setup and check if arguments were passed in """
    parser = set_parser()
    # no args provided, display help text
    if len(args) == 1:
        parser.print_help()
    else:
        parse_args(parser.parse_args(), parser)
    return

if __name__ == "__main__":
    args = sys.argv
    main(args)
