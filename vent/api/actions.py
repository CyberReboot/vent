import os

from api.plugins import Plugin
from api.templates import Template

class Action:
   """ Handle actions in menu """
   def __init__(self, **kargs):
       self.plugin = Plugin(**kargs)

   @staticmethod
   def add():
       return

   @staticmethod
   def remove():
       return

   @staticmethod
   def start():
       return

   @staticmethod
   def stop():
       return

   @staticmethod
   def clean():
       return

   def build(self, repo=None, tool=None, group=None, enabled=True, branch="master", version="HEAD"):
       build_all = True
       response = (True, None)
       if repo:
           # build all tools in the manifest for this repo for this branch and this version
           # if enabled is True, only build ones that are enabled
           build_all = False
           matches = {}
           self.plugin.build = True
           self.plugin.branch = branch
           self.plugin.version = version
           template = Template(template=self.plugin.manifest)
           sections = template.sections()
           for section in sections[1]:
               # !! TODO if tool
               # !! TODO if group
               store = False
               if template.option(section, 'namespace')[1].split('/')[-1] == repo \
                  and template.option(section, 'branch')[1] == branch \
                  and template.option(section, 'version')[1] == version:
                   if enabled:
                       if template.option(section, 'enabled')[1] == 'yes':
                           store = True
                   else:
                       store = True
               if store:
                   matches[section] = {}
                   matches[section]['image_name'] = template.option(section, 'image_name')[1]
                   matches[section]['path'] = template.option(section, 'path')[1]

           for match in matches:
               os.chdir(matches[match]['path'])
               response = self.plugin.checkout()
               if response[0]:
                   template = self.plugin.build_image(template, matches[match]['path'], matches[match]['image_name'], match)
       if tool:
           # build all tools in the manifest for this tool name for this branch and this version
           # if enabled is True, only build ones that are enabled
           build_all = False
       if group:
           # build all tools in the manifest that belong to this group name for this branch and this version
           # if enabled is True, only build ones that are enabled
           build_all = False
       if build_all:
           # get all tools in the manifest and build them for this branch and this version
           # if enabled is True, only build ones that are enabled
           pass
       template.write_config()
       return response

   @staticmethod
   def backup():
       return

   @staticmethod
   def restore():
       return

   @staticmethod
   def show():
       # repos, core, tools, images, built, running, etc.
       return

   @staticmethod
   def configure():
       # tools, core, etc.
       return

   @staticmethod
   def system_info():
       return

   @staticmethod
   def system_conf():
       return

   @staticmethod
   def system_commands():
       # restart, shutdown, upgrade, etc.
       return

   @staticmethod
   def logs():
       return

   @staticmethod
   def help():
       return
