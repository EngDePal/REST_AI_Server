"""Plug-In Manager for robot logic modules attaching to the core server application"""
#Importing necessary libraries
from importlib import util
import os
from plugins.plugin_interface import PluginInterface

#Plug-In Manager handling robot logic
class RobotLogicManager:

    #Initalizes the Plug-In Manager
    def __init__(self):
        #Path is subject to change (improving project structure)
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.plugin_directory = os.path.join(self.dir_path, "plugins")
        self.plugin_list = []

    #Prints all instantiated plugins
    def show_all_running_plugins(self):
        print(PluginInterface.show_all_plugins(PluginInterface))

    #Source: https://gist.github.com/dorneanu/cce1cd6711969d581873a88e0257e312
    #Allows for the dynamic loading of modules
    def load_module(self, path):
        #Gets filename from path
        name = os.path.split(path)[-1]
        #Creates a module spec
        spec = util.spec_from_file_location(name, path)
        #Creates a module from spec
        module = util.module_from_spec(spec)
        #Importing the Module
        spec.loader.exec_module(module)
        return module
    

rlm = RobotLogicManager()
module = rlm.load_module("/Users/dennispal00/Documents/Masterarbeit_THI/REST_AI_Server/packages/plugins/test_plugin.py")
print(module.run())