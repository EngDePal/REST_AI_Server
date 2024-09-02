"""Test Plugin implementing the Plugin-Interface"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#Importing the interface
from packages.plugins.utils.plugin_interface import PluginInterface
#Importing command objects
from packages.plugins.utils.commands import *

#This is a test plug-in
class TestPlugin(PluginInterface):

    #Constructor not necessary here
    def __init__(self):
        pass
    
    #Returns default state
    #Used during plug-in loading
    def setup(self):

        print("Setting up the Telepath Commands plug-in...")

        state = dict()
        state["counter"] = 1

        print("Telepath Commands active.")
        return state
    
    #Checks every command possible in a total of 6 steps
    def run(self, state):

        #Application state is restored from DB info
        #State is passed as a dict
        self.counter = state["counter"]

        #Command generation
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

        #Generation of state dictionary
        app_state = dict()
        if self.counter < 6:
            self.counter += 1
        app_state["counter"] = self.counter

        return command, app_state
