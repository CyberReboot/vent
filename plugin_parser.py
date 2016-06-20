#!/usr/bin/env python2.7

import ConfigParser
import os
import shutil
import sys

def add_plugins(plugin_url):
    # !! TODO keep track of changes so that they can be removed later on
    try:
        os.system("git config --global http.sslVerify false")
        os.system("cd /var/lib/docker/data/plugin_repos/ && git clone "+plugin_url)
        if ".git" in plugin_url:
            plugin_url = plugin_url.split(".git")[0]
        plugin_name = plugin_url.split("/")[-1]
        subdirs = [x[0] for x in os.walk("/var/lib/docker/data/plugin_repos/"+plugin_name)]
        check_modes = True
        for subdir in subdirs:
            try:
                if subdir.startswith("/var/lib/docker/data/plugin_repos/"+plugin_name+"/collectors/"):
                    recdir = subdir.split("/var/lib/docker/data/plugin_repos/"+plugin_name+"/collectors/")[1]
                    # only go one level deep, and copy recursively below that
                    if not "/" in recdir:
                        dest = "/var/lib/docker/data/collectors/"+recdir
                        if os.path.exists(dest):
                            shutil.rmtree(dest)
                        shutil.copytree(subdir, dest)
                elif subdir.startswith("/var/lib/docker/data/plugin_repos/"+plugin_name+"/plugins/"):
                    recdir = subdir.split("/var/lib/docker/data/plugin_repos/"+plugin_name+"/plugins/")[1]
                    # only go one level deep, and copy recursively below that
                    if not "/" in recdir:
                        dest = "/var/lib/docker/data/plugins/"+recdir
                        if os.path.exists(dest):
                            shutil.rmtree(dest)
                        shutil.copytree(subdir, dest)
                elif subdir.startswith("/var/lib/docker/data/plugin_repos/"+plugin_name+"/visualization/"):
                    recdir = subdir.split("/var/lib/docker/data/plugin_repos/"+plugin_name+"/visualization/")[1]
                    # only go one level deep, and copy recursively below that
                    if not "/" in recdir:
                        dest = "/var/lib/docker/data/visualization/"+recdir
                        if os.path.exists(dest):
                            shutil.rmtree(dest)
                        shutil.copytree(subdir, dest)
                elif subdir == "/var/lib/docker/data/plugin_repos/"+plugin_name+"/visualization":
                    # only files, not dirs
                    dest = "/var/lib/docker/data/visualization/"
                    for (dirpath, dirnames, filenames) in os.walk(subdir):
                        for filename in filenames:
                            shutil.copyfile(subdir+"/"+filename, dest+filename)
                elif subdir == "/var/lib/docker/data/plugin_repos/"+plugin_name+"/templates":
                    # only files, not dirs
                    dest = "/var/lib/docker/data/templates/"
                    for (dirpath, dirnames, filenames) in os.walk(subdir):
                        for filename in filenames:
                            if filename == "modes.template":
                                check_modes = False
                                shutil.copyfile(subdir+"/"+filename, dest+filename)
                            if filename == "core.template":
                                read_config = ConfigParser.RawConfigParser()
                                read_config.read('/var/lib/docker/data/templates/core.template')
                                write_config = ConfigParser.RawConfigParser()
                                write_config.read(subdir+"/"+filename)
                                write_sections = write_config.sections()
                                for section in write_sections:
                                    if read_config.has_section(section):
                                		read_config.remove_section(section)
                                    read_config.add_section(section)
                                    recdir = "/var/lib/docker/data/plugin_repos/"+plugin_name+"/core/"+section
                                    dest1 = "/var/lib/docker/data/core/"+section
                                    print recdir
                                    print dest1
                                    if os.path.exists(dest1):
                                        shutil.rmtree(dest1)
                                    print section
                                    shutil.copytree(recdir, dest1)
                                with open('/var/lib/docker/data/templates/core.template', 'w') as configfile:
                					read_config.write(configfile)
                                print subdir
                                
            except:
                print sys.exc_info()
        # update modes.template if it wasn't copied up to include new plugins
        if check_modes:
            files = [x[2] for x in os.walk("/var/lib/docker/data/templates")][0]
            config = ConfigParser.RawConfigParser()
            config.read('/var/lib/docker/data/templates/modes.template')
            plugin_array = config.options("plugins")
            plugins = {}
            for f in files:
                f_name = f.split(".template")[0]
                if f_name != "README.md" and not f_name in plugin_array and f_name != "modes":
                    config.set("plugins", f_name, "all")
            with open('/var/lib/docker/data/templates/modes.template', 'w') as configfile:
                config.write(configfile)
    except:
        pass

def remove_plugins(plugin_url):
    try:
        if ".git" in plugin_url:
            plugin_url = plugin_url.split(".git")[0]
        plugin_name = plugin_url.split("/")[-1]
        repo_subdirs = [x[0] for x in os.walk("/var/lib/docker/data/plugin_repos/"+plugin_name)]
        sys_subdirs = [x[0] for x in os.listdir("/var/lib/docker/data/")]
        for r_sub in repo_subdirs:
            #get name of sub-directory without prefix
            repo_dir = r_sub.split("/var/lib/docker/data/plugin_repos/"+plugin_name+"/")[0]
            if repo_dir.startswith("core/"):
                sys_subdirs = [x[0] for x in os.listdir("/var/lib/docker/data/core/")]
                repo_dir.split("core/")
            elif repo_dir.startswith("plugins/"):
                sys_subdirs = [x[0] for x in os.listdir("/var/lib/docker/data/plugins/")]
                repo_dir.split("plugins/")
            elif repo_dir.startswith("visualization/"):
                sys_subdirs = [x[0] for x in os.listdir("/var/lib/docker/data/visualization/")]
                repo_dir.split("visualization/")
            elif repo_dir.startswith("collectors/"):
                sys_subdirs = [x[0] for x in os.listdir("/var/lib/docker/data/collectors/")]
                repo_dir.split("collectors/")
            elif repo_dir.startswith("templates/"):
                continue
            else: 
                raise error(plugin_url)
 
            if repo_dir != ""
                for s_sub in sys_subdirs:
                    if repo_dir in s_sub:
                        shutil.rmtree(s_sub)
                        repo_subdirs.remove(r_sub) 


    except error as e:
        print "failed to remove plugin " + e
        
    #remove git repo once done    
    shutil.rmtree("/var/lib/docker/data/plugin_repos/"+plugin_name)

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
