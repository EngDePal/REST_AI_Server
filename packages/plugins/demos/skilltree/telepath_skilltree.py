"""This is a demo of an ontology featuring a video game skill tree of robot commands"""
#Fixing imports
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#Importing owlready2
from owlready2 import get_ontology, sync_reasoner
#importing the commands
from packages.plugins.utils.commands import *
#Importing interface
from packages.plugins.utils.plugin_interface import PluginInterface
#Parsing string and converting to json
import json

class Skilltree(PluginInterface):

    #Init loads the ontology
    def __init__(self):
        path = "/Users/dennispal00/Documents/Masterarbeit_THI/REST_AI_Server/packages/plugins/demos/skilltree/skilltree_ontology.rdf"
        self.ontology = get_ontology(path).load()
        print("Ontology can be accessed.")

    #The skilltree will start at level one
    def setup(self):
        
        print("Setting up Telepath Skilltree plug-in...")

        initial_level = 1
        setup_file = dict()
        setup_file["level"] = initial_level

        print("Telepath Skilltree active.")

        return setup_file
    
    def run(self, state: dict):
        
        #Access the current level and query the corresponding individual
        level_individual = self.ontology.search_one(hasValue=state["level"])
        #Checks the corresponding skill and gets data
        unlocked_skills = level_individual.unlocks
        skill = unlocked_skills
        name = skill.hasName

        #Generating command new command
        command = self.generate_command(skill)

        #Generating new state through reasoning
        #Only a previous_level property is explicitely modeled
        #The reverse property must be found by the reasoner

        #Start the reasoner
        with self.ontology:
            sync_reasoner()

        #An index error will occur on the last iteration
        try:
            next_level = list(level_individual.nextLevel)[0]

        except IndexError as e:
            print(e)
            new_state = state
        else:
            new_state = dict()
            new_state["level"] = next_level.hasValue
        
        return command, new_state

    #Creates the correct command based on ontology information
    def generate_command(self, skill: object):
        name = skill.hasName
        if name == "LOG":
            command = CommandLOG()
            return command
        elif name == "EXIT":
            command = CommandEXIT()
            return command
        elif name == "INFO":
            command = CommandINFO()
            return command
        elif name == "PTP":
            json_string = skill.hasFrame
            frame = json.loads(json_string)
            command = CommandPTP(frame)
            return command
        elif name == "LIN":
            json_string = skill.hasFrame
            frame = json.loads(json_string)
            command = CommandLIN(frame)
            return command
        elif name == "CIRC":
            aux_string = skill.hasAuxiliaryFrame
            dest_string = skill.hasDestination
            auxiliaryFrame = json.loads(aux_string)
            destination = json.loads(dest_string)
            command = CommandCIRC(auxiliaryFrame, destination)
            return command
