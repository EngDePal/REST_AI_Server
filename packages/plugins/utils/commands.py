"""Implements command classes as output of every robot plugin as specified in the API"""
from abc import ABC, abstractmethod
import json

class Command(dict, ABC):

    #If input is not given, frames default to this command
    #Should raise a error, due to faulty media type


    #Initialize a custom dict with the shared keys for command, parameters and type
    #If input is not given, frames default to {}
    #Should raise a error, due to faulty media type
    def __init__(self, command: str, frame: dict = {}, auxiliaryFrame: dict = {}, destination: dict = {}):

        #Checks input frames
        if command in ["LIN", "PTP"]:
            #Checks for potential input frames
            self.verify_frame(frame)
        elif command == "CIRC":
            self.verify_frame(auxiliaryFrame)
            self.verify_frame(destination)


        super().__init__()
        self.allowed_commands = ["EXIT", "LOG", "SEND", "PTP", "CIRC", "LIN"]

        if command not in self.allowed_commands:
            raise InvalidCommandError(command)
        else:
            self["command"] = command
            self["parameters"] = dict()
            self["parameters"]["type"] = "Param" + str(command)

        self.set_specifics(frame, auxiliaryFrame, destination)

    #This method is implemented by command subclasses to add unique elements
    @abstractmethod
    def set_specifics(self, frame: dict, auxiliaryFrame: dict, destination: dict):
        pass
    
    #Checks the frame for correct keys and datatypes
    def verify_frame(self, frame: dict):

        frame_elements = ["a", "b", "c", "x", "y", "z"]
        if not isinstance(frame, dict): 
            raise TypeError(f"Expected frame to be a dict, but got {type(frame)}.")
        
        for element in frame_elements:
            try:
                #Must be int or float
                if type(frame[element]) not in [int, float]:
                    raise TypeError
            except KeyError as e:
                print(e)
                break
    
    #Returns the command istelf
    def return_dict(self):
        # Convert instance to dictionary
        return dict(self)

    #Returns itself as a json object
    def return_json(self):
        return json.dumps(self.return_dict())

"Throws an error if a command is not EXIT, LOG, SEND, PTP, CIRC or LIN"
class InvalidCommandError(Exception):

    def __init__(self, command):
        self.allowed_commands = ["EXIT", "LOG", "SEND", "PTP", "CIRC", "LIN"]
        if command not in self.allowed_commands:
            super().__init__(f"Invalid command: {command}. Expected one of: ['EXIT', 'LOG', 'SEND', 'PTP', 'CIRC', 'LIN']")

#Class for EXIT commands
class CommandEXIT(Command):

    def __init__(self):
        super().__init__(command = "EXIT", frame = {}, auxiliaryFrame = {}, destination = {})

    #No specifics for EXIT
    def set_specifics(self, frame: dict, auxiliaryFrame: dict, destination: dict):
        pass

#Class for LOG commands
class CommandLOG(Command):

    def __init__(self):
        super().__init__(command = "LOG", frame = {}, auxiliaryFrame = {}, destination = {})

    #No specifics for LOG
    def set_specifics(self, frame: dict, auxiliaryFrame: dict, destination: dict):
        pass

#Class for SEND commands
class CommandSEND(Command):

    def __init__(self):
        super().__init__(command = "SEND", frame = {}, auxiliaryFrame = {}, destination = {})

    #No specifics for EXIT
    def set_specifics(self, frame: dict, auxiliaryFrame: dict, destination: dict):
        pass

#Class for LIN commands
class CommandLIN(Command):

    def __init__(self, frame: dict):
        super().__init__(command = "LIN", frame = frame, auxiliaryFrame = {}, destination = {})

    #Frame with 6 parameters
    def set_specifics(self, frame: dict, auxiliaryFrame: dict, destination: dict):
        self["parameters"]["Frame"] = frame

#Class for PTP commands
class CommandPTP(Command):

    def __init__(self, frame: dict):
        super().__init__(command = "PTP", frame = frame, auxiliaryFrame = {}, destination = {})

    #Frame with 6 parameters
    def set_specifics(self, frame: dict, auxiliaryFrame: dict, destination: dict):
        self["parameters"]["Frame"] = frame

#Class for CIRC commands
class CommandCIRC(Command):

    def __init__(self, auxiliaryFrame: dict, destination: dict):
        super().__init__(command = "CIRC", frame = {}, auxiliaryFrame = auxiliaryFrame, destination = destination)

    #2 Frames with 6 parameters each
    def set_specifics(self, frame: dict, auxiliaryFrame: dict, destination: dict):
        self["parameters"]["auxiliaryFrame"] = auxiliaryFrame
        self["parameters"]["destination"] = destination