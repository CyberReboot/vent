import os

from api.plugins import Plugin

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

   def build(self, repo=None, name=None, group=None, enabled="yes", branch="master", version="HEAD"):
       args = locals()
       options = ['image_name', 'path']
       status = (True, None)
       self.plugin.build = True
       self.plugin.branch = branch
       self.plugin.version = version
       sections, template = self.plugin.constraint_options(args, options)
       for section in sections:
           os.chdir(sections[section]['path'])
           status = self.plugin.checkout()
           if status[0]:
               template = self.plugin.build_image(template, sections[section]['path'], sections[section]['image_name'], section)
       template.write_config()
       return status

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
