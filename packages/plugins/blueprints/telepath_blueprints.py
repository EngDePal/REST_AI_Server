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

class OntologyReasoning(PluginInterface):

    #Init loads the ontology
    def __init__(self):
        #This ontologyb is based on the product model ontology and describes a house
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
        product_name = self.product_selection()

        #Querying the ontology for all parts without precondition
        parts_list = product_name.hasPart
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
        state["Product"] = product_name.name #Product name for later checking
        state["Current part"] = first_part.name #Name of current part
        state["Finished actions"] = list() #Only instructions of the current part
        state["Finished parts"] = list() #Finished part to avoid repeating steps

        return state

    #This method selects the next building step by querying the ontology
    #It then returns a robot command and the application state
    def run(self, state: dict):
        
        #State includes the current part and its finished actions
        #First step: Check the part actions

        #Get the product instance from the ontology
        for product in self.ontology.Product.instances():
            if product.name == state["Product"]:
                self.current_product = product
        
        #Get the current part
        for part in self.current_product.hasPart:
            if  part.name == state["Current part"]:
                self.current_part = part

        #Get the correct instructions for this product
        for instruction in self.current_part.hasInstruction:
            if instruction.hasProductConstraint == self.current_product:
                self.current_instruction = instruction

        #Get a list of the instruction actions
        list_of_actions = self.current_instruction.hasAction
        #Check for the first action: the one with no precondition
        #Actions are modeled deteminuístically in this ontology
        #So there is a clear order with only one starting action
        actions_with_precondition = self.ontology.ActionWithPrecondition.instances()
        actions_without_precondition = list()
        for action in list_of_actions:
            if action not in actions_with_precondition:
                actions_without_precondition.append(action)

        #Determine the current action
        self.current_action = actions_without_precondition[0]
        check = True
        #Checking the action chain modeled in the ontology
        #Until the action is not part of the finished actions list
        # while self.current_action.name not in state["Finished actions"]:
        #     if self.current_action.hasEnabledAction is not []:
        #         self.current_action = self.current_action.hasEnabledAction

        

        # print(self.current_product)
        # print(self.current_part)
        # print(self.current_instruction)
        # print(self.current_action)
        

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
    
    #Generates a state variable for the plugin
    #def generate_state(self, 

#Testing
reasoner = OntologyReasoning()
x = reasoner.setup()
reasoner.run(x)

