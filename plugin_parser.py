#!/usr/bin/env python2.7

import ConfigParser
import os
import shutil
import sys

"""
add_plugins(plugin_url)

PARAMETERS: plugin_url - a https link to a git repository as a string

DESCRIPTION: download plugins from plugin_url into a plugin_repos directory, 
copying files from plugin_repos to the correct location in local Vent filesystem.
after copying files, update templates
"""

def add_plugins(plugin_url):
    try:
        if not ".git" in plugin_url:
            plugin_url = plugin_url + ".git"
        plugin_name = plugin_url.split("/")[-1].split(".git")[0]
        if plugin_name == "":
            print "No plugins added, url is not formatted correctly"
            print "Please use a git url, e.g. https://github.com/CyberReboot/vent-plugins.git"
            return
        #check to see if plugin already exists in filesystem
        if os.path.isdir("/var/lib/docker/data/plugin_repos/"+plugin_name):
            print plugin_name+" already exists. Not installing."
            return
        os.system("git config --global http.sslVerify false")
        os.system("cd /var/lib/docker/data/plugin_repos/ && git clone "+plugin_url)
        #check to see if repo was cloned correctly
        if not os.path.isdir("/var/lib/docker/data/plugin_repos/"+plugin_name):
            print plugin_name+" did not install. Is this a git repository?"
            return

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
                    else:
                        namespace = recdir.split("/")[0]
                        if not os.path.isfile("/var/lib/docker/data/plugin_repos/"+plugin_name+"/templates/"+namespace+".template"):
                            shutil.rmtree("/var/lib/docker/data/plugins/"+namespace)
                            print "Warning! Plugin namespace has no template. Not installing "+namespace
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
                            elif filename == "core.template":
                                read_config = ConfigParser.RawConfigParser()
                                read_config.read('/var/lib/docker/data/templates/core.template')
                                write_config = ConfigParser.RawConfigParser()
                                write_config.read(subdir+"/"+filename)
                                write_sections = write_config.sections()
                                for section in write_sections:
                                    read_config.remove_section(section)
                                    read_config.add_section(section)
                                    recdir = "/var/lib/docker/data/plugin_repos/"+plugin_name+"/core/"+section
                                    dest1 = "/var/lib/docker/data/core/"+section
                                    if os.path.exists(dest1):
                                        shutil.rmtree(dest1)
                                    shutil.copytree(recdir, dest1)
                                with open('/var/lib/docker/data/templates/core.template', 'w') as configfile:
                                    read_config.write(configfile)
                            else:
                                namespace = filename.split(".")[0]
                                if os.path.isdir("/var/lib/docker/data/plugin_repos/"+plugin_name+"/plugins/"+namespace):
                                    shutil.copyfile(subdir+"/"+filename, dest+filename)
                                else:
                                    print "Warning! Plugin template with no corresponding plugins to install. Not installing "+namespace+".template"
                                    os.remove("var/lib/docker/data/templates/"+filename)
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
                if f_name != "README.md" and not f_name in plugin_array and f_name != "modes":
                    config.set("plugins", f_name, "all")
            with open('/var/lib/docker/data/templates/modes.template', 'w') as configfile:
                config.write(configfile)
        # check if files copied over correctly
        for subdir in subdirs:
            if os.path.isdir(subdir):
                directory = subdir.split("/var/lib/docker/data/plugin_repos/"+plugin_name+"/")[0]
                if subdir == "/var/lib/docker/data/plugin_repos/"+plugin_name:
                    continue
                if not os.path.isdir("/var/lib/docker/data/"+directory):
                    print "Failed to install "+plugin_name+" resource: "+directory
                    os.system("sudo rm -rf /var/lib/docker/data/plugin_repos/"+plugin_name)
                    return
        #resources installed correctly. Building...
        os.system("/bin/sh /data/build_images.sh")
        return  
    except:
        pass

"""
Name: remove_plugins(plugin_url)

Parameters: plugin_url - a https link to a git repository as a string

Description: Find plugin repo in plugin_repos directory based on name in plugin_url.
Delete all elements of the plugin in local Vent filesystem, update templates to reflect changes,
then delete the plugin from plugin_repos.
"""
def remove_plugins(plugin_url):
    try:
        if ".git" in plugin_url:
            plugin_url = plugin_url.split(".git")[0]
        plugin_name = plugin_url.split("/")[-1]
        if not os.path.isdir("/var/lib/docker/data/plugin_repos/"+plugin_name):
            print "Plugin is not installed. Not removing "+plugin_name
            return
        repo_subdirs = [x[0] for x in os.walk("/var/lib/docker/data/plugin_repos/"+plugin_name, topdown=False)]
        sys_subdirs = [x[0] for x in os.walk("/var/lib/docker/data/")]
        repo_dir = ""
        namespace = ""
        #looks for installed items in repo, deletes them. Updates templates to reflect changes
        for r_sub in repo_subdirs:
            if plugin_name+"/core/" in r_sub:
                sys_subdirs = [x[0] for x in os.walk("/var/lib/docker/data/core")]
                repo_dir = r_sub.split(plugin_name+"/core/")[1]
                namespace = "core"
            elif plugin_name+"/plugins/" in r_sub:
                sys_subdirs = [x[0] for x in os.walk("/var/lib/docker/data/plugins")]
                repo_dir = r_sub.split(plugin_name+"/plugins/")[1]
                element = repo_dir.split("/")
                if len(element) == 1:
                    #no subdirectories - no plugins to be deleted in namespace. -> Delete namespace
                    namespace = element[0]
                    config = ConfigParser.RawConfigParser()
                    for dirpath, dirnames, files in os.walk("/var/lib/docker/data/plugins/"+namespace):
                        if not dirnames:
                            os.remove("/var/lib/docker/data/templates/"+namespace+".template")
                            config.read("/var/lib/docker/data/templates/modes.template")
                            config.remove_option("plugins", namespace)
                            with open("/var/lib/docker/data/templates/modes.template", 'w') as configfile:
                                config.write(configfile)
                            shutil.rmtree(dirpath)
                else:
                    #there are plugins to be removed
                    namespace = element[0]
                    plugin = element[1]
                    element = "/".join(element[0:2])
                    if element != "":
                        for s_sub in sys_subdirs:
                            if element in s_sub:
                                config = ConfigParser.RawConfigParser()
                                config.read("/var/lib/docker/data/templates/"+namespace+".template")
                                config.remove_section(plugin)
                                with open("/var/lib/docker/data/templates/"+namespace+".template", 'w') as configfile:
                                    config.write(configfile)
                                shutil.rmtree(s_sub)   
                continue
            elif plugin_name+"/visualization" in r_sub:
                names = os.listdir("/var/lib/docker/data/visualization")
                has_subdir = False
                for name in names:
                    has_subdir = os.path.isdir(os.path.join("/var/lib/docker/data/visualization/",name))
                    if has_subdir:
                        break
                #there are no visualizations, cleans up extra files e.g. README.md
                if not has_subdir:
                    os.remove("/var/lib/docker/data/templates/visualization.template")
                    for dirpath, dirnames, files in os.walk("/var/lib/docker/data/visualization/"):
                        for file in files:
                            os.remove("/var/lib/docker/data/visualization/"+file)
                    continue
                sys_subdirs = [x[0] for x in os.walk("/var/lib/docker/data/visualization/")]
                repo_dir = r_sub.split(plugin_name+"/visualization/")[1]
                namespace = "visualization"
            elif plugin_name+"/collectors/" in r_sub:
                names = os.listdir("/var/lib/docker/data/collectors")
                has_subdir = False
                for name in names:
                    has_subdir = os.path.isdir("/var/lib/docker/data/collectors/"+name)
                    if has_subdir:
                        break
                #there are not collectors, cleans up extra files e.g. README.md
                if not has_subdir:
                    for dirpath, dirnames, files in os.walk("/var/lib/docker/data/collectors/"):
                        for file in files:
                            os.remove("/var/lib/docker/data/collectors/"+file)
                    continue
                sys_subdirs = [x[0] for x in os.walk("/var/lib/docker/data/collectors/")]
                repo_dir = r_sub.split(plugin_name+"/collectors/")[1]
                namespace = "collectors"
            else:
                continue
            #handles case if item removed is not in plugins/
            for s_sub in sys_subdirs:
                if repo_dir in s_sub:
                    shutil.rmtree(s_sub)
                    config = ConfigParser.RawConfigParser()
                    if os.path.exists("/var/lib/docker/data/templates/"+namespace+".template"):
                        config.read("/var/lib/docker/data/templates/"+namespace+".template")
                        config.remove_section(repo_dir.split("/")[0])
                        with open("/var/lib/docker/data/templates/"+namespace+".template", 'w') as configfile:
                            config.write(configfile)  
                    config.read("/var/lib/docker/data/templates/modes.template")
                    config.remove_option("plugins", namespace)
                    with open("/var/lib/docker/data/templates/modes.template", 'w') as configfile:
                        config.write(configfile)
        #remove git repo once done    
        shutil.rmtree("/var/lib/docker/data/plugin_repos/"+plugin_name)
        print "Successfully removed Plugin: "+plugin_name

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
