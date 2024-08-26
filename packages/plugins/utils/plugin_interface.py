"""This abstract class serves as an interface for all plug-ins"""
#Importing modules
from abc import ABC, abstractmethod
import os
import inspect

#File names must adhere to the naming convention telepath_"filename"
#There must only be one class in this file, which must implement the interface
#However the plugin can consist of several other files of course
class PluginInterface(ABC):

    plugins = []

    #Can be used to setup the application
    @abstractmethod
    def __init__(self):
        pass

    #For every class that inherits from the current,
    #the class name will be added to plugins
    #Source: https://gist.github.com/dorneanu/cce1cd6711969d581873a88e0257e312
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.plugins.append(cls)

    #Returns a list of all instantiated subclasses
    @classmethod
    def show_all_plugins(cls):
        return cls.plugins
    
    #Returns the path of the class
    @classmethod
    def show_path(cls):
        path = inspect.getfile(cls)
        return os.path.realpath(path)

    #The core method of every plug-in
    #Will be called by the server
    #Will always receive the last known application state as a dict
    #The form of state depends on the plugin design
    @abstractmethod
    def run(self, state: dict):
        #Must always return a tuple: command object (as specified by the API), application state (dict)
        #Command object can be imported as a seprate class inside 'plugins'
        #State must allow the plugin to resume functionality seemlessly
        #State will also be passed as a dict: plugin must access relevant keys
        pass

    #Must return a starting state during plugin selection
    #State must be a dict
    @abstractmethod
    def setup(self):
        pass

