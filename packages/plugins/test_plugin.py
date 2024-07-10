#Importing the interface
from plugin_interface import PluginInterface

#This is a test plug-in
class TestPlugin(PluginInterface):

    def __init__(self):
        self.counter = 1
    
    #Checks every command possible in a total of 6 steps
    def run(self):

        if self.counter == 1:
            command == {"command" : "LIN",
                     "parameters" : {
                         "type" : "paramLIN",
                         "frame" : {
                             "a" : 0,
                             "b" : 0,
                             "c" : 0,
                             "x" : 300,
                             "z" : 200,
                             "y" : 123
                             }
                        }
                     }
        elif self.counter == 2:
            command == {"command" : "PTP",
                     "parameters" : {
                         "type" : "paramPTP",
                         "frame" : {
                             "a" : 50,
                             "b" : 60,
                             "c" : 15,
                             "x" : 200,
                             "z" : 200,
                             "y" : 123
                             }
                        }
                     }
        elif self.counter == 3:
            command == {"command" : "CIRC",
                     "parameters" : {
                         "type" : "paramPTP",
                         "auxiliaryFrame" : {
                             "a" : 22,
                             "b" : 60,
                             "c" : 15,
                             "x" : 150,
                             "z" : 100,
                             "y" : 123
                             },
                        "destination": {
                             "a" : 0,
                             "b" : 0,
                             "c" : 0,
                             "x" : 0,
                             "z" : 0,
                             "y" : 0

                        }
                        }
                     }
        elif self.counter == 4:
            command = {
                "type" : "LOG"
            }
        elif self.counter == 5:
            command = {
                "type" : "INFO"
            }
        elif self.counter == 6:
            command = {
                "type" : "EXIT"
            }
        if self.counter < 6:
            self.counter += 1
        return command

#Testing import
test = TestPlugin()
print(test.show_all_plugins())