"""Plugin Manager for robot logic modules attaching to the core server application"""
#Importing necessary libraries
import importlib
import importlib.util
import os
import sys
from packages.plugins.utils.plugin_interface import PluginInterface
import inspect
import pkgutil

#Plugin Manager handling robot logic
class RobotLogicManager:

    #Initalizes the Plugin Manager
    def __init__(self):

        #Plugin directory
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.plugin_directory = os.path.join(self.dir_path, "plugins")

        #Allows for plugin discovery
        #Allows Python to search in the plugin directory
        sys.path.append(self.plugin_directory)

        #Allows Python to search in newly added plugins-subdirectories
        for root, dirs, files in os.walk(self.plugin_directory):
            if root not in sys.path:
                sys.path.append(root)
        
        #Creates a dict of discovered plugins and their paths
        self.dicscovered_plugins = self.dicscover_plugins()

        #Mapping of loaded (cached) plugins by  names to the corresponding module
        self.plugin_mapping = dict()

    #Source: https://gist.github.com/dorneanu/cce1cd6711969d581873a88e0257e312
    #Allows for the dynamic loading of modules
    def load_module(self, path: str):
        #Gets filename from path
        name = os.path.split(path)[-1]
        #Creates a module spec
        spec = importlib.util.spec_from_file_location(name, path)
        #Creates a module from spec
        module = importlib.util.module_from_spec(spec)
        #Importing the Module
        spec.loader.exec_module(module)

        #Module management for further operations
        self.register_plugin(name, module)
        
        return name
    
    #Creates and returns an instance of the main class of the plugin
    def instantiate_plugin(self, module: PluginInterface):
        #There should be only one class inheriting from PluginInterface
        for name, object in inspect.getmembers(module):
        #Check if the object is a class and subclasses PluginInterface
            if inspect.isclass(object) and issubclass(object, PluginInterface) and object != PluginInterface:
                #Instantiate the class
                plugin_instance = object()

        return plugin_instance
    
    #Creates and returns a plugin instance
    def create_instance(self, plugin_name: str):
        module = self.get_plugin(plugin_name)
        instance = self.instantiate_plugin(module)
        return instance

    
    #Discovers all plugins adhering to naming convention in the plugin directory
    #Naming convention: telepath_plugin_name (Telepath is the software name)
    def dicscover_plugins(self):
        discovered_plugins = {
            name: module_finder.find_spec(name).origin
            for module_finder, name, ispkg in pkgutil.iter_modules()
            if name.startswith('telepath_')
        }
        
        return discovered_plugins
    
    #Getter Method for discovered plugins
    def get_discovery(self):
        return self.dicscovered_plugins

    #Creates a mapping of plugin_names to loaded_modules
    def register_plugin(self, plugin_name: str, module: type):

        #Allows the server to cache modules, which are already in use  
        self.plugin_mapping[plugin_name] = module

    #Returns the correct plugin module
    #According to the provided name
    def get_plugin(self, plugin_name: str):
        module = self.plugin_mapping[plugin_name]
        return module