#!/usr/bin/env python2.7

import base64
import ConfigParser
import os
import re
import shutil
import subprocess
import sys

from helpers.paths import PathDirs

"""
add_plugins(path_dirs, plugin_url)

PARAMETERS: path_dirs - a PathDirs object which stores info about filesystem for plugin addition/removal
            plugin_url - a https link to a git repository as a string

DESCRIPTION: download plugins from plugin_url into a plugin_repos directory,
copying files from plugin_repos to the correct location in local Vent filesystem.
after copying files, update templates
"""

def add_plugins(path_dirs, plugin_url, user=None, pw=None):
    try:
        if not ".git" in plugin_url:
            plugin_url = plugin_url + ".git"
        plugin_name = plugin_url.split("/")[-1].split(".git")[0]
        if plugin_name == "":
            print("No plugins added, url is not formatted correctly")
            print("Please use a git url, e.g. https://github.com/CyberReboot/vent-plugins.git")
            return
        # check to see if plugin already exists in filesystem
        if os.path.isdir(path_dirs.plugin_repos+"/"+plugin_name):
            print(plugin_name+" already exists. Not installing.")
            return
        os.system("git config --global http.sslVerify false")
        if not user and not pw:
            os.system("cd "+path_dirs.plugin_repos+"/ && git clone --recursive "+plugin_url)
        else:
            new_plugin_url = plugin_url.split("https://")[-1]
            os.system("cd "+path_dirs.plugin_repos+"/ && git clone --recursive https://"+user+":"+pw+"@"+new_plugin_url)
        # check to see if repo was cloned correctly
        if not os.path.isdir(path_dirs.plugin_repos+"/"+plugin_name):
            print(plugin_name+" did not install. Is this a git repository?")
            return

        subdirs = [x[0] for x in os.walk(path_dirs.plugin_repos+"/"+plugin_name)]
        check_modes = True
        for subdir in subdirs:
            try:
                if subdir.startswith(path_dirs.plugin_repos+"/"+plugin_name+"/collectors/"):
                    recdir = subdir.split(path_dirs.plugin_repos+"/"+plugin_name+"/collectors/")[-1]
                    # only go one level deep, and copy recursively below that
                    if not "/" in recdir:
                        dest = path_dirs.collectors_dir+"/"+recdir
                        if os.path.exists(dest):
                            shutil.rmtree(dest)
                        shutil.copytree(subdir, dest)
                elif subdir.startswith(path_dirs.plugin_repos+"/"+plugin_name+"/plugins/"):
                    recdir = subdir.split(path_dirs.plugin_repos+"/"+plugin_name+"/plugins/")[-1]
                    # only go one level deep, and copy recursively below that
                    if not "/" in recdir:
                        dest = path_dirs.plugins_dir+"/"+recdir
                        if os.path.exists(dest):
                            shutil.rmtree(dest)
                        shutil.copytree(subdir, dest)
                    else:
                        # makes sure that every namespace has a corresponding template file
                        namespace = recdir.split("/")[0]
                        if not os.path.isfile(path_dirs.plugin_repos+"/"+plugin_name+"/templates/"+namespace+".template"):
                            print("Warning! Plugin namespace has no template. Not installing "+namespace)
                            shutil.rmtree(path_dirs.plugins_dir+namespace)
                elif subdir.startswith(path_dirs.plugin_repos+"/"+plugin_name+"/visualization/"):
                    recdir = subdir.split(path_dirs.plugin_repos+"/"+plugin_name+"/visualization/")[-1]
                    # only go one level deep, and copy recursively below that
                    if not "/" in recdir:
                        dest = path_dirs.vis_dir+"/"+recdir
                        if os.path.exists(dest):
                            shutil.rmtree(dest)
                        shutil.copytree(subdir, dest)
                # elif subdir == path_dirs.plugin_repos+"/"+plugin_name+"/visualization":
                #     # only files, not dirs
                #     dest = path_dirs.vis_dir+"/"
                #     for (dirpath, dirnames, filenames) in os.walk(subdir):
                #         for filename in filenames:
                #             shutil.copyfile(subdir+"/"+filename, dest+filename)
                elif subdir == path_dirs.plugin_repos+"/"+plugin_name+"/templates":
                    # only files, not dirs
                    dest = path_dirs.template_dir
                    for (dirpath, dirnames, filenames) in os.walk(subdir):
                        for filename in filenames:
                            if filename == "modes.template":
                                check_modes = False
                                shutil.copyfile(subdir+"/"+filename, dest+filename)
                            elif filename == "collectors.template":
                                shutil.copyfile(subdir+"/"+filename, dest+filename)
                            elif filename == "visualization.template":
                                shutil.copyfile(subdir+"/"+filename, dest+filename)
                            elif filename == "core.template":
                                read_config = ConfigParser.RawConfigParser()
                                # needed to preserve case sensitive options
                                read_config.optionxform=str
                                read_config.read(path_dirs.template_dir + 'core.template')
                                write_config = ConfigParser.RawConfigParser()
                                # needed to preserve case sensitive options
                                write_config.optionxform=str
                                write_config.read(subdir+"/"+filename)
                                write_sections = write_config.sections()
                                for section in write_sections:
                                    read_config.remove_section(section)
                                    read_config.add_section(section)
                                    recdir = path_dirs.plugin_repos+"/"+plugin_name+"/core/"+section
                                    dest1 = path_dirs.core_dir+"/"+section
                                    if os.path.exists(dest1):
                                        shutil.rmtree(dest1)
                                    shutil.copytree(recdir, dest1)
                                with open(path_dirs.template_dir + 'core.template', 'w') as configfile:
                                    read_config.write(configfile)
                            else:
                                # makes sure that every template file has a corresponding namespace in filesystem
                                namespace = filename.split(".")[0]
                                if os.path.isdir(path_dirs.plugin_repos+"/"+plugin_name+"/plugins/"+namespace):
                                    shutil.copyfile(subdir+"/"+filename, dest+filename)
                                else:
                                    print("Warning! Plugin template with no corresponding plugins to install. Not installing "+namespace+".template")
                                    os.remove(path_dirs.plugin_repos+"/"+plugin_name+"/templates/"+filename)
            except Exception as e:
                pass
        # update modes.template if it wasn't copied up to include new plugins
        if check_modes:
            files = [x[2] for x in os.walk(path_dirs.base_dir + "templates")][0]
            config = ConfigParser.RawConfigParser()
            # needed to preserve case sensitive options
            config.optionxform=str
            config.read(path_dirs.template_dir + 'modes.template')
            plugin_array = config.options("plugins")
            plugins = {}
            for f in files:
                f_name = f.split(".template")[0]
                if f_name != "README.md" and not f_name in plugin_array and f_name != "modes" and (os.path.isdir(path_dirs.plugins_dir+f_name) or os.path.isdir(path_dirs.base_dir+f_name)):
                    config.set("plugins", f_name, "all")
            with open(path_dirs.template_dir + 'modes.template', 'w') as configfile:
                config.write(configfile)
        # check if files copied over correctly
        for subdir in subdirs:
            if os.path.isdir(subdir):
                directory = subdir.split(path_dirs.plugin_repos+"/"+plugin_name+"/")[0]
                if subdir == path_dirs.plugin_repos+"/"+plugin_name:
                    continue
                if not os.path.isdir(path_dirs.base_dir + directory):
                    print("Failed to install "+plugin_name+" resource: "+directory)
                    os.system("sudo rm -rf "+path_dirs.plugin_repos+"/"+plugin_name)
                    return
        # resources installed correctly. Building...
        os.system("/bin/sh "+path_dirs.scripts_dir+"build_images.sh --basedir "+path_dirs.base_dir[:-1])
    except Exception as e:
        pass

"""
Name: remove_plugins(plugin_url)

Parameters: path_dirs - a PathDirs object which stores info about filesystem for plugin addition/removal
            plugin_url - a https link to a git repository as a string

Description: Find plugin repo in plugin_repos directory based on name in plugin_url.
Delete all elements of the plugin in local Vent filesystem, update templates to reflect changes,
then delete the plugin from plugin_repos.
"""
def remove_plugins(path_dirs, plugin_url):
    try:
        if ".git" in plugin_url:
            plugin_url = plugin_url.split(".git")[0]
        plugin_name = plugin_url.split("/")[-1]
        if not os.path.isdir(path_dirs.plugin_repos+"/"+plugin_name):
            print("Plugin is not installed. Not removing "+plugin_name)
            return
        repo_subdirs = [x[0] for x in os.walk(path_dirs.plugin_repos+"/"+plugin_name, topdown=False)]
        sys_subdirs = [x[0] for x in os.walk(path_dirs.base_dir)]
        repo_dir = ""
        namespace = ""
        #looks for installed items in repo, deletes them. Updates templates to reflect changes
        for r_sub in repo_subdirs:
            if plugin_name+"/core/" in r_sub:
                sys_subdirs = [x[0] for x in os.walk(path_dirs.core_dir)]
                repo_dir = r_sub.split(plugin_name+"/core/")[-1]
                namespace = "core"
            elif plugin_name+"/plugins/" in r_sub:
                sys_subdirs = [x[0] for x in os.walk(path_dirs.base_dir + "plugins")]
                repo_dir = r_sub.split(plugin_name+"/plugins/")[-1]
                element = repo_dir.split("/")
                if len(element) == 1:
                    #no subdirectories - no plugins to be deleted in namespace. -> Delete namespace
                    namespace = element[0]
                    for dirpath, dirnames, files in os.walk(path_dirs.plugins_dir + namespace):
                        if not dirnames:
                            os.remove(path_dirs.template_dir + namespace + ".template")
                            config = ConfigParser.RawConfigParser()
                            # needed to preserve case sensitive options
                            config.optionxform=str
                            config.read(path_dirs.template_dir + "modes.template")
                            config.remove_option("plugins", namespace)
                            with open(path_dirs.template_dir + "modes.template", 'w') as configfile:
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
                                # needed to preserve case sensitive options
                                config.optionxform=str
                                config.read(path_dirs.template_dir + namespace + ".template")
                                config.remove_section(plugin)
                                with open(path_dirs.template_dir + namespace + ".template", 'w') as configfile:
                                    config.write(configfile)
                                shutil.rmtree(s_sub)
                continue
            elif plugin_name+"/visualization" in r_sub:
                names = os.listdir(path_dirs.vis_dir)
                has_subdir = False
                for name in names:
                    has_subdir = os.path.isdir(os.path.join(path_dirs.vis_dir + "/",name))
                    if has_subdir:
                        break
                #there are no visualizations, cleans up extra files e.g. README.md
                if not has_subdir:
                    os.remove(path_dirs.template_dir + "visualization.template")
                    for dirpath, dirnames, files in os.walk(path_dirs.vis_dir+"/"):
                        for file in files:
                            os.remove(path_dirs.vis_dir+"/"+file)
                    continue
                sys_subdirs = [x[0] for x in os.walk(path_dirs.vis_dir + "/")]
                repo_dir = r_sub.split(plugin_name+"/visualization/")[-1]
                namespace = "visualization"
            elif plugin_name+"/collectors/" in r_sub:
                names = os.listdir(path_dirs.collectors_dir)
                has_subdir = False
                for name in names:
                    has_subdir = os.path.isdir(path_dirs.collectors_dir + "/"+name)
                    if has_subdir:
                        break
                #there are no collectors, cleans up extra files e.g. README.md
                if not has_subdir:
                    for dirpath, dirnames, files in os.walk(path_dirs.collectors_dir + "/"):
                        for file in files:
                            os.remove(path_dirs.collectors_dir+"/"+file)
                    continue
                sys_subdirs = [x[0] for x in os.walk(path_dirs.collectors_dir + "/")]
                repo_dir = r_sub.split(plugin_name+"/collectors/")[-1]
                namespace = "collectors"
            else:
                continue
            #handles case if item removed is not in plugins/
            for s_sub in sys_subdirs:
                if repo_dir in s_sub:
                    shutil.rmtree(s_sub)
                    if os.path.exists(path_dirs.template_dir + namespace + ".template"):
                        config = ConfigParser.RawConfigParser()
                        # needed to preserve case sensitive options
                        config.optionxform=str
                        config.read(path_dirs.template_dir + namespace + ".template")
                        config.remove_section(repo_dir.split("/")[0])
                        with open(path_dirs.template_dir + namespace + ".template", 'w') as configfile:
                            config.write(configfile)
                        config = ConfigParser.RawConfigParser()
                        # needed to preserve case sensitive options
                        config.optionxform=str
                        config.read(path_dirs.template_dir + "modes.template")
                        config.remove_option("plugins", namespace)
                        with open(path_dirs.template_dir + "modes.template", 'w') as configfile:
                            config.write(configfile)
                        break
        #remove git repo once done
        shutil.rmtree(path_dirs.plugin_repos+"/"+plugin_name)
        print("Successfully removed Plugin: "+plugin_name)

    except Exception as e:
        pass

# Update images for removed plugins
def update_images(path_dirs):
    images = []
    try:
        # Note - If grep finds nothing it returns exit status 1 (error). So, using grep first, awk second.
        images = subprocess.check_output(" docker images | grep '/' | awk \"{print \$1}\" ", shell=True).split("\n")
    except Exception as e:
        pass
    for image in images:
        image = image.split(" ")[0]
        if "core/" in image or "visualization/" in image or "collectors/" in image:
            if not os.path.isdir(path_dirs.base_dir + image):
                os.system("docker rmi "+image)
        else:
            if not os.path.isdir(path_dirs.plugins_dir + image):
                os.system("docker rmi "+image)

if __name__ == "__main__":
    path_dirs = PathDirs()

    if len(sys.argv) == 8:
        path_dirs = PathDirs(base_dir=sys.argv[6], data_dir=sys.argv[7])
        sys.argv = sys.argv[:-2]

    # change base dir for tests
    if len(sys.argv) == 5:
        path_dirs = PathDirs(base_dir=sys.argv[3], data_dir=sys.argv[4])
        sys.argv = sys.argv[:-2]

    if len(sys.argv) == 3:
        if sys.argv[1] == "update_plugins":
            remove_plugins(path_dirs, sys.argv[2])
            add_plugins(path_dirs, sys.argv[2])
            update_images(path_dirs)
        elif sys.argv[1] == "add_plugins":
            add_plugins(path_dirs, sys.argv[2])
        elif sys.argv[1] == "remove_plugins":
            remove_plugins(path_dirs, sys.argv[2])
            update_images(path_dirs)
        else:
            print("invalid plugin type to parse")
    # accepts username and password passed in from vcontrol. WARNING: should ONLY work for vcontrol
    elif len(sys.argv) == 6:
        user = sys.argv[3]
        pw = re.escape(base64.b64decode(sys.argv[4]))
        if sys.argv[1] == "update_plugins":
            remove_plugins(path_dirs, sys.argv[2])
            add_plugins(path_dirs, sys.argv[2], user, pw)
            update_images(path_dirs)
        elif sys.argv[1] == "add_plugins":
            add_plugins(path_dirs, sys.argv[2], user, pw)
        else:
            print("invalid plugin type to parse")
            sys.exit(10)
    else:
        print("Invalid number of arguments")
        sys.exit(20)
