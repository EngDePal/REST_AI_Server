"""This is plugin generates commands by querying and reasoning an ontology, which models the structure of a product part by part"""
#Fixing imports
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#Importing owlready2
from owlready2 import get_ontology, sync_reasoner
#importing the commands
from plugins.utils.commands import *
#Importing interface
from plugins.utils.plugin_interface import PluginInterface
#Parsing string and converting to json
import json

class Blueprint(PluginInterface):

    #Init loads the ontology
    def __init__(self):
        #This ontology is based on the product model ontology and describes a house
        path = "/Users/dennispal00/Documents/Masterarbeit_THI/REST_AI_Server/packages/plugins/blueprints/house_builder.rdf"
        self.ontology = get_ontology(path).load()
        print("Ontology can be accessed.")

        #Syncing reasoner
        with self.ontology:
            sync_reasoner()
        print("Reasoner active.")

    #The initial state of the plugin is determined by the parts of the house
    #That can be assembled without any preconditions
    #In this example it will be the foundation of the house
    def setup(self):

        #Allowing the user to decide, which product to built
        product = self.product_selection()

        #Querying the ontology for all parts without precondition
        parts_list = product.hasPart
        #So far the PartWithoutPrecondition class does not seem to work properly
        #Instead we will search for the parts with conditions and remove them frome the parts list
        parts_with_precondition = self.ontology.PartWithPrecondition.instances()
        parts_without_precondition = list()
        for part in parts_list:
            if part not in parts_with_precondition:
                parts_without_precondition.append(part)

        #Even if there are several elements in the list,
        #the initial setup will always select the first part
        #to generate the initial state
        first_part = parts_without_precondition[0]
        state = dict()
        #State information
        state["Product"] = product.name #Product name for later checking
        state["Current part"] = first_part.name #Name of current part
        state["Finished actions"] = list() #Only instructions of the current part
        state["Finished parts"] = list() #Finished part to avoid repeating steps

        return state

    #This method selects the next building step by querying the ontology
    #It then returns a robot command and the application state
    def run(self, state: dict):

        #Get the product instance from the ontology
        for product in self.ontology.Product.instances():
            if product.name == state["Product"]:
                self.current_product = product
        
        #Decision about the active part

        #If the current part has been marked as finished in a previous step
        #We will get the next one from the ontology
        if state["Current part"] in state["Finished parts"]:
            self.current_part = self.get_next_part(self.current_product, state)
            #Returns None if all parts have been assembled
            #The plugin then returns an exit command
            if self.current_part is None:
                exit_command = CommandEXIT()
                return exit_command
        #Else we will directly grab the part instance
        else:
            #Get the current part
            for part in self.current_product.hasPart:
                if  part.name == state["Current part"]:
                    self.current_part = part

        #Get the correct action
        current_action = self.get_next_action(self.current_part, self.current_product, state["Finished actions"])
        
        #Extracting the command
        command = self.generate_command(current_action)

        #Creating a new state variable
        state = self.generate_state(state, current_action, self.current_part)
        
        return command, state

    #Returns the instance of the product to built after user selection
    def product_selection(self):
        
        #Access the product class and its instances
        product_class = self.ontology.Product
        product_instances = product_class.instances()
        available_products = dict()
        
        #Gatrhers the names of the instances
        print("The following blueprints are available: ")
        for instance in product_instances:
            print(instance.name)
            available_products[instance.name] = instance

        #Allowing and checing user input
        # user_input = input("Please select the product to be built: ")
        # allowed_input = False
        # while allowed_input == False:
        #     try:
        #         product_to_build = available_products[user_input]
        #     except KeyError:
        #         user_input = input("Wrong input. Please try again: ")
        #     else:
        #         allowed_input = True

        #To ease production
        product_to_build = self.ontology.sketchHouse
            
        return product_to_build
    

    
    #Extracts ontology information like frame and command type and returns a formatted command
    def generate_command(self, action: object):
        type = action.hasCommand
        command = dict()

        if type == "LOG":
            command = CommandLOG()

        elif type == "EXIT":
            command = CommandEXIT()

        elif type == "INFO":
            command = CommandINFO()

        elif type == "PTP":
            json_string = action.hasFrame
            frame = json.loads(json_string)
            command = CommandPTP(frame)

        elif type == "LIN":
            json_string = action.hasFrame
            frame = json.loads(json_string)
            command = CommandLIN(frame)

        elif type == "CIRC":
            aux_string = action.hasAuxiliaryFrame
            dest_string = action.hasDestination
            auxiliaryFrame = json.loads(aux_string)
            destination = json.loads(dest_string)
            command = CommandCIRC(auxiliaryFrame, destination)
        
        return command
    
    #Generates a new state
    def generate_state(self, old_state: dict, current_action: object, current_part: object):
        
        #Fist step: Add the current action to the list of finished actions
        new_state = old_state
        new_state["Finished actions"].append(current_action.name)

        #Second step: Check wether all actions of this part are completed
        counter = 0
        for action in current_part.hasAction:
            if action.name not in new_state["Finished actions"]:
                counter += 1

        #If this is true the current part will be added as well
        if counter == 0:
            new_state["Finished parts"].append(self.current_part.name)
        #In the next run the system will then automatically select the next part
        
        return new_state
        
    
    #Based on the provided part and a list of finished actions, the correct next action will be returned
    #Also returns whether all actions of this part are completed or not
    def get_next_action(self, part: object, product: object, finished_actions: list):
        
        #Get the correct instructions for this product
        for instruction in part.hasInstruction:
            if instruction.hasProductConstraint == product:
                current_instruction = instruction

        #Get a list of the instruction actions
        list_of_actions = current_instruction.hasAction
        #Check for the first action: the one with no precondition
        #Actions are modeled deteminuístically in this ontology
        #So there is a clear order with only one starting action
        actions_with_precondition = self.ontology.ActionWithPrecondition.instances()
        actions_without_precondition = list()
        for action in list_of_actions:
            if action not in actions_with_precondition:
                actions_without_precondition.append(action)

        #Determine the current action
        current_action = actions_without_precondition[0]
        #Checking the action chain modeled in the ontology
        #Until the action is not part of the finished actions list
        check = True

        while check:
            if current_action.name in finished_actions:
                next_action = current_action.hasEnabledAction
                if next_action is None:
                    current_action = next_action
                else:
                    check = False
            else:
                check = False

        return current_action
    
    #Returns the next allowed part from the ontology
    def get_next_part(self, product: object, state: dict):
        
        #Preparation

        #Get list of all product parts
        part_list = product.hasPart

        #Creates a list of unfinished parts for reference
        unfinished_parts = list()
        for part in part_list:
            if part.name not in state["Finished parts"]:
                unfinished_parts.append(part)

        #Searches for all parts without preconditions
        parts_with_precondition = self.ontology.PartWithPrecondition.instances()
        parts_without_precondition = list()
        for part in part_list:
            if part not in parts_with_precondition:
                parts_without_precondition.append(part)

        #Three stage search algorithm
        possible_parts = list()
        stage_two_list = list()

        #Stage I
        #Parts without any condition are checked first
        #If one has not been finished yet, it will be added to the part list
        for part_without_precondition in parts_without_precondition:
            if part_without_precondition in unfinished_parts:
                possible_parts.append(part_without_precondition)

        #Stage II
        #If the list remins empty, we will check the parts
        #Which only have elements from parts_without_conditions marked as necessary parts
        if len(possible_parts) == 0:
            #Part in parts
            for part_without_precondition in parts_without_precondition:
                enabled_part_list = part_without_precondition.hasEnabledPart
                for enabled_part in enabled_part_list:
                    #Checks every enabled part for its requirements
                    #If the requirements are exclusively
                    condition_check = 0
                    condition_list = enabled_part.hasNecessaryPart
                    for condition in condition_list:
                        if condition not in parts_without_precondition:
                            condition_check += 1
                    if condition_check == 0 and enabled_part in unfinished_parts:
                        possible_parts.append(enabled_part)
                    if condition_check == 0:
                        stage_two_list.append(enabled_part)


        #Stage III
        #If the list still remains empty, we will check the rest of the parts
        if len(possible_parts) == 0:
            remaining_parts_list = part_list
            #Remove parts of stage I
            for part in parts_without_precondition:
                remaining_parts_list.remove(part)
            #Remove results of stage II
            for part in stage_two_list:
                remaining_parts_list.remove(part)         
            #Calling recursive method to find possible parts
            search_results = self.recursive_search(remaining_parts_list)
            for result in search_results:
                possible_parts.append(result)

        #If no part has been found, no action will be returned
        #This will lead to an Exit Command
        current_part = None
        #If parts have been found one will be randomly selected
        #This will help to demonstrate the non-scripted nature of the application
        if len(possible_parts) != 0:
            #Random selection
            current_part = None
            
        return current_part
    
    def recursive_search(self, part_list: list):
        search_result = list()

        return search_result
    
#Testing
reasoner = Blueprint()
init = reasoner.setup()
# init["Finished actions"].append("prepareFoundationConstruction")
# init["Finished actions"].append("startFoundationConstruction")
# init["Finished actions"].append("drawingFoundation")
# init["Finished parts"].append("foundation")

state = init
print("Inital state:")
print(state)
for i in range(1, 10):
    command, state = reasoner.run(state)
    print("Results run "+str(i) + ":")
    print(command)
    print(state)

