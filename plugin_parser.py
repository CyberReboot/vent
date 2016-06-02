#!/usr/bin/env python2.7

import ConfigParser
import os
import shutil
import sys

def add_plugins(plugin_url):
    # !! TODO keep track of changes so that they can be removed later on
    try:
        os.system("git config --global http.sslVerify false")
        os.system("cd /tmp && git clone "+plugin_url)
        if ".git" in plugin_url:
            plugin_url = plugin_url.split(".git")[0]
        plugin_name = plugin_url.split("/")[-1]
        subdirs = [x[0] for x in os.walk("/tmp/"+plugin_name)]
        check_modes = True
        for subdir in subdirs:
            try:
                if subdir.startswith("/tmp/"+plugin_name+"/collectors/"):
                    recdir = subdir.split("/tmp/"+plugin_name+"/collectors/")[1]
                    # only go one level deep, and copy recursively below that
                    if not "/" in recdir:
                        dest = "/var/lib/docker/data/collectors/"+recdir
                        if os.path.exists(dest):
                            shutil.rmtree(dest)
                        shutil.copytree(subdir, dest)
                elif subdir.startswith("/tmp/"+plugin_name+"/plugins/"):
                    recdir = subdir.split("/tmp/"+plugin_name+"/plugins/")[1]
                    # only go one level deep, and copy recursively below that
                    if not "/" in recdir:
                        dest = "/var/lib/docker/data/plugins/"+recdir
                        if os.path.exists(dest):
                            shutil.rmtree(dest)
                        shutil.copytree(subdir, dest)
                elif subdir.startswith("/tmp/"+plugin_name+"/visualization/"):
                    recdir = subdir.split("/tmp/"+plugin_name+"/visualization/")[1]
                    # only go one level deep, and copy recursively below that
                    if not "/" in recdir:
                        dest = "/var/lib/docker/data/visualization/"+recdir
                        if os.path.exists(dest):
                            shutil.rmtree(dest)
                        shutil.copytree(subdir, dest)
                elif subdir == "/tmp/"+plugin_name+"/visualization":
                    # only files, not dirs
                    dest = "/var/lib/docker/data/visualization/"
                    for (dirpath, dirnames, filenames) in os.walk(subdir):
                        for filename in filenames:
                            shutil.copyfile(subdir+"/"+filename, dest+filename)
                elif subdir == "/tmp/"+plugin_name+"/templates":
                    # only files, not dirs
                    dest = "/var/lib/docker/data/templates/"
                    for (dirpath, dirnames, filenames) in os.walk(subdir):
                        for filename in filenames:
                            shutil.copyfile(subdir+"/"+filename, dest+filename)
                            if filename == "modes.template":
                                check_modes = False
            except:
                pass
        # update modes.template if it wasn't copied up to include new plugins
        if check_modes:
            files = [x[2] for x in os.walk("/var/lib/docker/data/templates")][0]
            config = ConfigParser.RawConfigParser()
            config.read('/var/lib/docker/data/templates/modes.template')
            plugin_array = config.options("plugins")
            plugins = {}
            for f in files:
                f_name = f.split(".template")[0]
                if f_name != "README.md" and not f_name in plugin_array:
                    config.set("plugins", f_name, "all")
            with open('/var/lib/docker/data/templates/modes.template', 'w') as configfile:
                config.write(configfile)
        shutil.rmtree("/tmp/"+plugin_name)
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
