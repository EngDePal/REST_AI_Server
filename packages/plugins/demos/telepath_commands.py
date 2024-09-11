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
                    "x" : 498.7,
                    "y" : 436.5,
                    "z" : 478,
                    "a" : -1.6,
                    "b" : 0.03,
                    "c" : 3.0,
                             }
            command = CommandLIN(frame=frame)
        elif self.counter == 2:
            frame = {
                    "x" : 520.7,
                    "y" : 325.5,
                    "z" : 400.0,
                    "a" : -1.6,
                    "b" : 0.03,
                    "c" : 3.0,
                            }
            command = CommandPTP(frame)

        elif self.counter == 3:
            auxiliaryFrame = {
                            "x" : 510,
                            "y" : 370.5,
                            "z" : 400.0,
                            "a" : -1.6,
                            "b" : 0.03,
                            "c" : 3.0,
                             }
            destination =   {
                            "x" : 498.7,
                            "y" : 436.5,
                            "z" : 478,
                            "a" : -1.6,
                            "b" : 0.03,
                            "c" : 3.0,
                             }
            command = CommandCIRC(auxiliaryFrame = auxiliaryFrame, destination=destination)
                       
        elif self.counter == 4:
            command = CommandLOG()
        elif self.counter == 5:
            command = CommandSEND()
        elif self.counter == 6:
            command = CommandEXIT()

        #Generation of state dictionary
        app_state = dict()
        if self.counter < 6:
            self.counter += 1
        app_state["counter"] = self.counter

        return command, app_state
