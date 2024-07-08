"""This abstract class serves as an interface for all plug-ins"""
#Importing from abc for abstraction
from abc import ABC, abstractmethod

class PluginInterface(ABC):

    #The core method of every plug-in
    #Will be called by the server
    #Free to take in various inputs
    def operation(self, *args, **kwargs):
        #must always return a command object as specified by the API
        #Command object can be imported as a seprate class inside 'plugins'
        return command
