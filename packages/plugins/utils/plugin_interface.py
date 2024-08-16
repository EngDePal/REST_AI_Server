"""This abstract class serves as an interface for all plug-ins"""
#Importing modules
from abc import ABC, abstractmethod
import os
import inspect

class PluginInterface(ABC):

    plugins = []

    @abstractmethod
    def __init__(self):
        pass

    # For every class that inherits from the current,
    # the class name will be added to plugins
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
    #Will always receive the last known application state
    #The form of state depends on the plugin design
    @abstractmethod
    def run(self, state: dict):
        #Must always return a tuple of a command object as specified by the API
        #As well as application state dict
        #State must allow the plugin to resume functionality seemlessly
        #State will also be passed as a dict: plugin must access relevant keys
        #Command object can be imported as a seprate class inside 'plugins'
        pass

    #Must return a starting state during plugin selection
    @abstractmethod
    def setup(self):
        #State must be a dict
        pass

