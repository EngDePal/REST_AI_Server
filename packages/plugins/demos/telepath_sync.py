"""This demo demonstrates a way to control two robots at once, which alternate in their requests"""
#Fixing imports
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#Import plugin architecture utilities
from packages.plugins.utils.plugin_interface import PluginInterface
from packages.plugins.utils.commands import *
#Import the MongoDB interface
from packages.plugins.utils.mongo_interface import MongoInterface
#Calculating distance
import math

class SynchronizedControl(PluginInterface):

    #Constructor
    def __init__(self):

        #Create an instance of the data manager
        self.mongo = MongoInterface()

        #This plugin needs two robots to work
        self.max_robot_count = 2

        #Available positions: two opposite corners of a 14 cm x 14 cm square
        self.pos1 = {
                    "x" : 500,
                    "y" : 160,
                    "z" : 320,
                    "a" : -90.18,
                    "b" : 1.49,
                    "c" : 173.94
                             }
        self.pos2 = {
                    "x" : 640,
                    "y" : 300,
                    "z" : 320,
                    "a" : -90.18,
                    "b" : 1.49,
                    "c" : 173.94
                             }
        
        #List of all tasks
        self.all_tasks = dict(self.define_tasks())

    
    #Set-up 
    def setup(self):

        #Creating the initial state
        state = dict()

        #If too many robots login, they will be given an EXIT command
        exit_condition = self.check_exit_condition()
        state["Exit condition"] = exit_condition

        #Only create the correct state, if there are not enough robots
        if exit_condition == False:

            #Here we will save a list of the synchronized robots
            state["Synced robots"] = self.get_clients()

            #If too many robots login, they will be given an EXIT command
            exit_condition = self.check_exit_condition()

            #Saving the tasks done by the robot
            state["Finished tasks"] = list()

            #Saving the robot role/position
            #Since this is just a proof of concept, there will be two pre-selected positions
            state["Position"] = self.select_position()

            #Check ability to start the operation
            state["Operational"] = self.check_operational_capability(state["Synced robots"])

        print("Sync plugin sucessfully set-up.")

        return state

    #Main method for robot control
    def run(self, state: dict):

        #Immediately log-out all unnecessary clients
        if state["Exit condition"]  == True:
            kick_state = {"Exit condition": True, "Logout state": "Succesful"}
            command = CommandEXIT()

            return command, kick_state
        
        updated_state = dict(state)

        #Update the client count first
        updated_state = dict(self.update_synced_clients(state))

        #Update the operational capability
        updated_state["Operational"] = self.check_operational_capability(updated_state["Synced robots"])

        #Check the operationl capability
        check = updated_state["Operational"]

        #If there are not enough clients logged in, the robot should not move
        if check == False:
            command = CommandSEND()
        
        #Else a new command is selected
        else:
            next_task = self.select_command(updated_state)

            #If tasks are still available
            if next_task != None:
                command = self.all_tasks[next_task]
            
                #Update state
                updated_state["Finished tasks"].append(next_task)
            
            #Otherwise Log-Out
            else:
                if "Wait" not in updated_state.keys():
                    updated_state["Wait"] = True

                #Wait before logging out, to allow the companion to catch this client's final tasks
                if updated_state["Wait"] == True:
                    command = CommandSEND()
                    updated_state["Wait"] = False
                elif state["Wait"] == False:
                    command = CommandEXIT()

        print("Results")
        print(command)
        print(updated_state)

        return command, updated_state

    #Selects a new command based on the robot position and finished assignments
    def select_command(self, state: dict):
        
        #Stage I: Get all task keys, which are not yet listed as finished by this client
        available_tasks = list()
        for key in self.all_tasks.keys():
            if key not in state["Finished tasks"]:
                available_tasks.append(key)
        
        print(f"Stage I: available tasks: {available_tasks}")

        #Stage II: Check the other client's finished tasks and remove them too

        #Get the companion's token
        second_token = ""
        for token in state["Synced robots"]:
            if token != state["token"]:
                second_token = token

        #Query the companion's app state
        collection = "app_state"
        query = {"token": second_token}
        results = self.mongo.query_data(collection, query)

        #Remove the finished tasks, if there are any
        try:
            result = results[0]
            companion_tasks = result["Finished tasks"]

            print(f"Companions finished tasks: {companion_tasks}")

            for task_key in companion_tasks:
                if task_key in available_tasks:
                    available_tasks.remove(task_key)

        except IndexError:
            print("Error")

        finally:
            
            print(f"Stage II Available tasks: {available_tasks}")
            if len(available_tasks) > 0:
                #Stage III: Select the task by prioritization
                position = state["Position"]
                recommended_task = self.prioritize_tasks(available_tasks, position)
            
            else:
                recommended_task = None
            
            print(f"Recommended task: {recommended_task}")

            return recommended_task

    #Prioritizes tasks based on the distance between robot position and target
    #Returns the recommended task
    def prioritize_tasks(self, available_tasks: list, position: dict):
        
        #Defaults to recommending the first task
        recommended_task = available_tasks[0]
        command = self.all_tasks[recommended_task]
        if isinstance(command, CommandLIN):
            frame = command["parameters"]["Frame"]
        elif isinstance(command, CommandPTP):
            frame = command["parameters"]["Frame"]
        elif isinstance(command, CommandCIRC):
            frame = command["parameters"]["destination"]
        base_distance = self.calculate_distance(frame, position)

        #Checking whether other tasks are better
        for task_key in available_tasks:
            #Get the frame
            command = self.all_tasks[task_key]
            if isinstance(command, CommandLIN):
                frame = command["parameters"]["Frame"]
            elif isinstance(command, CommandPTP):
                frame = command["parameters"]["Frame"]
            elif isinstance(command, CommandCIRC):
                frame = command["parameters"]["destination"]
            distance = self.calculate_distance(frame, position)
            if distance < base_distance:
                base_distance = distance
                recommended_task = task_key

        return recommended_task

    #Calculates the euclidean distance between the target frame and the client positions
    #This used for the optimization of task seletion
    def calculate_distance(self, target_frame: dict, client_position: dict):

        sum = 0

        for coordinate in ["x", "y", "z"]:
            num = (target_frame[coordinate] - client_position[coordinate])**2
            sum += num

        result = math.sqrt(sum)

        return result

    
    #Allows the user to select one of two positions for the robot
    def select_position(self):

        print("Robot selection for specific tasks will depend on their position.")

        pos1_status, pos2_status = self.verify_position()
        
        #Print the positions depending on the already registered robots
        print("Available positions:")
        if pos1_status == False and pos2_status == False:
            print(f"Position 1:\n{self.pos1}")
            print(f"Position 2:\n{self.pos2}")
            available_positions = {"1": self.pos1, "2": self.pos2}
        elif pos1_status == True and pos2_status == False:
            print(f"Position 2:\n{self.pos2}")
            available_positions = {"2": self.pos2}
        elif pos1_status == False and pos2_status == True:
            print(f"Position 1:\n{self.pos1}")
            available_positions = {"1": self.pos1}
        
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
    
    #Checks, if any positions have already been selected
    def verify_position(self):

        #First look up, which robots are logged into this plugin as well
        collection1 = "plugins"
        #Plug-In names end with .py
        query1 = {"plugin_name": "telepath_sync.py"}
        query_results1 = self.mongo.query_data(collection1, query1)

        #Conditions
        pos1_selected = False
        pos2_selected = False

        #Search for the app states of the clients using the plugin
        for result in query_results1:
            token = result["token"]
            collection2 = "app_state"
            query2 = {"token": token}
            query_results2 = self.mongo.query_data(collection2, query2)

            #Check the query results
            for client in query_results2:
                try:
                    if client["Position"] == self.pos1:
                        pos1_selected = True
                    elif client["Position"] == self.pos2:
                        pos2_selected = True
                except KeyError:
                    pass

        return pos1_selected, pos2_selected
    
    #Exit condition: 
    #If there are already two robots registered
    #This function will return True
    def check_exit_condition(self):
        
        collection = "plugins"
        #Plug-In names end with .py
        query = {"plugin_name": "telepath_sync.py"}
        robot_list = self.mongo.query_data(collection, query) 

        if len(robot_list) > 2:
            return True
        elif len(robot_list) <= 2:
            return False
        
    #Checks whether all necessary actors are logged in
    def get_clients(self):

        #Query all clients using the plug-in
        #Plug-In names end with .py
        collection1 = "plugins"
        query1 = {"plugin_name": "telepath_sync.py"}
        robot_list = self.mongo.query_data(collection1, query1)

        #Check whether any of these clients are about to be logged out
        #Get a list of these tokens
        forbidden_tokens = list()
        for robot in robot_list:
            collection2 = "app_state"
            query2 = {"token": robot["token"]}
            results = self.mongo.query_data(collection2, query2)
            for result in results:
                try:
                    if result["Exit condition"] == True:
                        forbidden_tokens.append(result["token"])
                except KeyError:
                    None

        #Get and return the allowed tokens
        tokens = list()
        for robot in robot_list:
            if robot["token"] not in forbidden_tokens:
                tokens.append(robot["token"])

        return tokens
    
    #Updates the state with the actual clients
    def update_synced_clients(self, state: dict):

        #Fist add the clients own token to the state, if not already done
        if state["token"] not in state["Synced robots"]:
            state["Synced robots"].append(state["token"])

        #Check the second clients token and append it
        tokens = self.get_clients()
        second_token = ""
        for token in tokens:
            if token != state["token"]:
                second_token = token
        if second_token != "":
            if second_token not in  state["Synced robots"]:
                state["Synced robots"].append(second_token)

        return state
    
    #Check ability to start the operation
    #Need a list of clients as input like state["Synced robots"]
    def check_operational_capability(self, active_client_list: list):

        #Check ability to start the operation
            if len(active_client_list) == 2:
                return True
            else:
                return False

    #Defines a total of six movement tasks
    def define_tasks(self):

        tasks = dict()
        
        #First task
        frame_one = {
                    "x" : 540,
                    "y" : 175,
                    "z" : 320,
                    "a" : -90.18,
                    "b" : 1.49,
                    "c" : 173.94
                             }
        command_one = CommandPTP(frame_one)
        tasks[1] = command_one
        
        #Second task
        frame_two = {
                    "x" : 500,
                    "y" : 230,
                    "z" : 320,
                    "a" : -90.18,
                    "b" : 1.49,
                    "c" : 173.94
                             }
        command_two = CommandPTP(frame_two)
        tasks[2] = command_two
        
        #Third task
        frame_three = {
                    "x" : 430,
                    "y" : 230,
                    "z" : 320,
                    "a" : -90.18,
                    "b" : 1.49,
                    "c" : 173.94
                             }
        command_three = CommandPTP(frame_three)
        tasks[3] = command_three
        
        #Fourth task
        frame_four = {
                    "x" : 640,
                    "y" : 215,
                    "z" : 320,
                    "a" : -90.18,
                    "b" : 1.49,
                    "c" : 173.94
                             }
        command_four = CommandPTP(frame_four)
        tasks[4] = command_four
        
        #Fifth task
        frame_five = {
                    "x" : 580,
                    "y" : 275,
                    "z" : 320,
                    "a" : -90.18,
                    "b" : 1.49,
                    "c" : 173.94
                             }
        command_five = CommandPTP(frame_five)
        tasks[5] = command_five
        
        #Sixth task
        frame_six = {
                    "x" : 500,
                    "y" : 300,
                    "z" : 320,
                    "a" : -90.18,
                    "b" : 1.49,
                    "c" : 173.94
                             }
        command_six = CommandPTP(frame_six)
        tasks[6] = command_six

        return tasks
        
        



        


