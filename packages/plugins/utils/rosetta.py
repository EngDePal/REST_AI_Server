"""Language adapter: serves as an API which allows for integration of plugins in other programming languagues"""
#UNTESTED!!!
#Plugin main class can just inherit Rosetta

#Importing plugin utilities
from plugins.utils.plugin_interface import PluginInterface
from plugins.utils.commands import *
#Allowing HTTP requests
import requests
import jsonschema
from jsonschema import validate

class Rosetta(PluginInterface):

    #Enter the server URL
    url = ""
    #Specifying acceptable input
    headers = {
    "Accept": "application/json"
    }

    #Main method of the class
    #Will be called by the server
    def run(self):

        #Calling all requests to populate variables
        self.request_command()
        self.request_frame()
        self.request_auxiliaryFrame()
        self.request_destination()

        #Calling corresponding command class
        if self.command == "EXIT":
            return CommandEXIT()
        elif self.command == "LOG":
            return CommandLOG()
        elif self.command == "LOG":
            return CommandINFO()
        elif self.command == "LIN":
            return CommandLIN(frame = self.frame)
        elif self.command == "PTP":
            return CommandPTP(frame = self.frame)
        elif self.command == "CIRC":
            return CommandCIRC(auxiliaryFrame=self.auxiliaryFrame, destination=self.destination)
        else:
            raise InvalidCommandError(self.command)
        
    
    #Exclusive use of GET commands to receive data from the server in a different languague

    #Get a command type: EXIT, LOG, INFO, PTP, LIN, CIRC
    def request_command(self):
        ending = "/command"
        total_url = self.url + ending
        if requests.get(total_url, headers = self.headers) in ["EXIT", "LOG", "INFO", "PTP", "LIN", "CIRC"]:
            json_response = requests.get(total_url, headers = self.headers)

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "command": {
                 "type": "string"
                }
            },
            "required": ["command"],
            "additionalProperties": False
        }

        try:
            validate(instance=json_response, schema=schema)
            print("JSON response is valid.")
        except jsonschema.exceptions.ValidationError as err:
            print("JSON response is invalid.")
            print(err)
        else: 
            self.command = json_response

    #Get a frame for LIN and PTP movements
    def request_frame(self):
        if self.command in ["LIN", "PTP"]:
            ending = "/frame"
            total_url = self.url + ending
            json_response = requests.get(total_url, headers = self.headers)

            schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
                "c": {"type": "number"},
                "x": {"type": "number"},
                "y": {"type": "number"},
                "z": {"type": "number"}
            },
            "required": ["a", "b", "c", "x", "y", "z"],
            "additionalProperties": False
            }
        
        try:
            validate(instance=json_response, schema=schema)
            print("JSON response is valid.")
        except jsonschema.exceptions.ValidationError as err:
            print("JSON response is invalid.")
            print(err)
        else: 
            self.frame = json_response

    #Get an auxiliary frame for CIRC movements
    def request_auxiliaryFrame(self):
        if self.command == "CIRC":
            ending = "/auxiliaryFrame"
            total_url = self.url + ending
            json_response = requests.get(total_url, headers = self.headers)

            schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
                "c": {"type": "number"},
                "x": {"type": "number"},
                "y": {"type": "number"},
                "z": {"type": "number"}
            },
            "required": ["a", "b", "c", "x", "y", "z"],
            "additionalProperties": False
            }
        
        try:
            validate(instance=json_response, schema=schema)
            print("JSON response is valid.")
        except jsonschema.exceptions.ValidationError as err:
            print("JSON response is invalid.")
            print(err)
        else: 
            self.auxiliaryFrame = json_response


    def request_destination(self):
        if self.command == "CIRC":
            ending = "/destination"
            total_url = self.url + ending
            json_response = requests.get(total_url, headers = self.headers)

            schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
                "c": {"type": "number"},
                "x": {"type": "number"},
                "y": {"type": "number"},
                "z": {"type": "number"}
            },
            "required": ["a", "b", "c", "x", "y", "z"],
            "additionalProperties": False
            }
        
        try:
            validate(instance=json_response, schema=schema)
            print("JSON response is valid.")
        except jsonschema.exceptions.ValidationError as err:
            print("JSON response is invalid.")
            print(err)
        else: 
            self.destination = json_response
