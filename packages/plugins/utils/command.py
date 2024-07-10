"""Defines the expected output of every robot logic module as specified in the API"""
class Command:

    #Please see the thesis for further info on the commands
    allowed_commands = ["EXIT", "PTP", "LIN", "CIRC", "INFO", "LOG"]

    #General Info about the various commands and their parameters
    #LIN and PTP: Robot target position is described as a frame of 6 values: (a, b, c) are degrees of rotation, (x, y, z) are translations along the axes
    #CIRC: Requires an intermediate point (auxiliaryFrame, see LIN and PTP) and a destination point (additional frame)
    #EXIT, INFO, LOG: No content of parameters except type (e.g. "paramEXIT")
    #Frames should adhere to the following key names: a, b, c, x, y, z
    # def __init__(self, command_name, **parameters):
    #     if command_name in self.allowed_commands:
    #         self.command = command_name
    #         self.type = "param" + str(self.command)
    #         return command_object
    
    # def check_parameters(self, **parameters):
    #     if self.command == "PTP" or "LIN":
    #         for key, value in parameters.items():
    #             if key == "frame":
    #                 self.frame = frame

            
            

            






        


