"""Test Plugin implementing the Plugin-Interface"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#Importing the interface
from plugins.utils.plugin_interface import PluginInterface
#Importing command objects
from plugins.utils.commands import *

#This is a test plug-in
class TestPlugin(PluginInterface):

    def __init__(self):
        self.counter = 1
    
    #Checks every command possible in a total of 6 steps
    def run(self):

        if self.counter == 1:
            frame = {
                    "a" : 0,
                    "b" : 0,
                    "c" : 0,
                    "x" : 300,
                    "z" : 200,
                    "y" : 123
                             }
            command = CommandLIN(frame=frame)
        elif self.counter == 2:
            frame = {
                    "a" : 50,
                    "b" : 60,
                    "c" : 15,
                    "x" : 200,
                    "z" : 200,
                    "y" : 123
                            }
            command = CommandPTP(frame)

        elif self.counter == 3:
            auxiliaryFrame = {
                             "a" : 22,
                             "b" : 60,
                             "c" : 15,
                             "x" : 150,
                             "z" : 100,
                             "y" : 123
                             }
            destination =   {
                             "a" : 0,
                             "b" : 0,
                             "c" : 0,
                             "x" : 0,
                             "z" : 0,
                             "y" : 0
                             }
            command = CommandCIRC(auxiliaryFrame = auxiliaryFrame, destination=destination)
                       
        elif self.counter == 4:
            command = CommandLOG()
        elif self.counter == 5:
            command = CommandINFO()
        elif self.counter == 6:
            command = CommandEXIT()
        if self.counter < 6:
            self.counter += 1
        return command
