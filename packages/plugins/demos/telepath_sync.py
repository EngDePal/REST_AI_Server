"""This demo demonstrates a way to command two robots at once"""
#Import plugin architecture utilities
from packages.plugins.utils.plugin_interface import PluginInterface
from packages.plugins.utils.commands import *
#Import the data manager
from packages.data_manager import DataManager

class SynchronizedControl(PluginInterface):

    #Constructor
    def __init__(self):

        #Create an instance of the data manager
        self.dm = DataManager()

        #This plugin needs two robots to work
        self.max_robot_count = 2

    
    #Set-up 
    def setup(self):

        #Creating the initial state
        state = dict()

        #Saving the token of the second robot
        state["Synced robot"] = list()

        exit_condition = self.check_exit_condition()
        if exit_condition == False:
            synced_robot = self.get_synchronized_robot()
            state["Synced robot"] = synced_robot

        #Saving the commands done by the robot
        state["Finished commands"] = list()
        #Saving the robot role/position
        #Since this is just a proof of concept, there will be two pre-selected positions
        state["Position"] = self.select_position()
        #Exit condition
        state["Exit condition"] = exit_condition

        return state

    #Main method for robot control
    def run(self, setup: dict):
        
        pass

    def generate_state(self):
        pass

    def generate_command(self):
        pass

    
    #Allows the user to select one of two positions for the robot
    def select_position(self):

        print("Robot selection for specific tasks will depend on their position.")
        
        #Available positions: two opposite corners of a 14 cm x 14 cm square
        pos1 = {
                    "a" : -100,
                    "b" : 0,
                    "c" : 180,
                    "x" : 200,
                    "y" : 355,
                    "z" : 350
                             }
        pos2 = {
                    "a" : -100,
                    "b" : 0,
                    "c" : 180,
                    "x" : 340,
                    "y" : 495,
                    "z" : 350
                             }
        
        available_positions = {1: pos1, 2: pos2}
        
        #Print the positions
        print("Available positions:")
        print(f"Position 1:\n{pos1}")
        print(f"Position 2:\n{pos2}")
        
        user_input = input("Please select a position by index: ")

        allowed_input = False
        while allowed_input == False:
            try:
                position = available_positions[user_input]
            except KeyError:
                user_input = input("Position not found. Please try again: ")
            else:
                allowed_input = True
                print("Position selection succesful.")
        
        return position
    
    #Retrieves the token of the synced robot
    def get_synchronized_robot(self):
        
        #First look up, which robots is logged into this plugin as well
        collection = "plugins"
        query = {"plugin_name": "telepath_sync"}
        synced_robot_list = self.dm.query_data(collection, query)

        if len(synced_robot_list) == 1:
            synced_robot = synced_robot_list[0]
        
        return synced_robot

    
    #Exit condition: 
    #If there are already two robots registered
    #This function will return True
    def check_exit_condition(self):
        
        collection = "plugins"
        query = {"plugin_name": "telepath_sync"}
        robot_list = self.dm.query_data(collection, query) 

        if len(robot_list) == 2:
            return True
        elif len(robot_list) < 2:
            return False
        else:
            raise Exception("Too many robots logged into the Sync Plug-in.")



