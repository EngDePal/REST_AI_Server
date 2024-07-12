"""Very basic plugin checks plugin loading withou dependencies"""
"""Evaluates all robot commands"""
#Does not yet implement any interface etc.

#Checks for the counter
def read_counter():

    try:
        with open('counter_storage.txt', 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 1

#Writes the counter so it can be persistent    
def write_counter(value: int):
    with open('counter_storage.txt', 'w') as file:
        file.write(str(value))

#Checks every command possible in a total of 6 steps
def run():

    counter = read_counter()

    if counter == 1:
        command = {"command" : "LIN",
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
    elif counter == 2:
        command = {"command" : "PTP",
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
    elif counter == 3:
            command = {"command" : "CIRC",
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
    elif counter == 4:
            command = {
                "type" : "LOG"
            }
    elif counter == 5:
            command = {
                "type" : "INFO"
            }
    elif counter == 6:
            command = {
                "type" : "EXIT"
            }

    if counter < 6:
            counter += 1
    else: counter = 1
    write_counter(counter)
    
    return command