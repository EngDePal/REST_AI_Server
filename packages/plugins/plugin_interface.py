"""This abstract class serves as an interface for all plug-ins"""
#Importing from abc for abstraction
from abc import ABC, abstractmethod
import os
from importlib import util
import traceback

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

    def show_all_plugins(cls):
        return cls.plugins

    #The core method of every plug-in
    #Will be called by the server
    #Free to take in various inputs
    @abstractmethod
    def run(self, **kwargs):
        #must always return a command object as specified by the API
        #Command object can be imported as a seprate class inside 'plugins'
        pass
