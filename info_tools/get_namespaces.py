#!/usr/bin/env python2.7

import argparse
import sys

def set_parser():
    """ initialize parser """
    parser = argparse.ArgumentParser(prog="get_namespaces")
    #parser.add_argument("-a", "--all",
    #                    help="print all of the namespaces installed",
    #                    action="store_true")
    parser.add_argument("-m", "--mimetypes",
                        help="print all of the mimetypes supported by the installed namespaces",
                        action="store_true")
    return parser

def parse_args(args, parser):
    """ parse arguments, and output based on arguments passed in """
    if args.mimetypes:
        # !! TODO
        # check templates and installed namespaces based on images built, also check modes
        print "foo"
        pass

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
