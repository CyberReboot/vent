#!/usr/bin/env python2.7

import os
import shutil
import sys

def add_plugins(plugin_url):
    try:
        # !! TODO right path, also parse out directories, and cleanup after
        os.system("git config --global http.sslVerify false")
        os.system("cd /tmp && git clone "+plugin_url)
        if ".git" in plugin_url:
            plugin_url = plugin_url.split(".git")[0]
        plugin_name = plugin_url.split("/")[-1]
        with open('/tmp/bar', 'w') as f:
            f.write(plugin_name)
        subdirs = [x[0] for x in os.walk("/tmp/"+plugin_name)]
        for subdir in subdirs:
            with open('/tmp/dirs', 'a') as f:
                f.write(subdir+"\n")
            src = "/tmp/"+plugin_name+"/"+subdir+"/*"
            if subdir == "/tmp/"+plugin_name+"/collectors":
                dest = "/var/lib/docker/data/collectors/"
                shutil.copytree(src, dest)
            elif subdir == "/tmp/"+plugin_name+"/plugins":
                dest = "/var/lib/docker/data/plugins/"
                shutil.copytree(src, dest)
            elif subdir == "/tmp/"+plugin_name+"/templates":
                pass
            elif subdir == "/tmp/"+plugin_name+"/visualization":
                dest = "/var/lib/docker/data/visualization/"
                shutil.copytree(src, dest)
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
