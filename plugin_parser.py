#!/usr/bin/env python2.7

import os
import sys

def add_plugins(plugin_url):
    try:
        # !! TODO right path, also parse out directories, and cleanup after
        os.system("cd /tmp && git clone "+plugin_url)
    except:
        pass

def remove_plugins(plugin_url):
    try:
        # !! TODO
        os.system("ls")
    except:
        pass

if __name__ == "__main__":
    if len(sys.argv) == 3:
        if sys.argv[1] == "add_plugins":
            add_plugins(sys.argv[2])
        elif sys.argv[1] == "remove_plugins":
            remove_plugins(sys.argv[2])
        else:
            print "invalid plugin type to parse"
    else:
        print "not enough arguments"
