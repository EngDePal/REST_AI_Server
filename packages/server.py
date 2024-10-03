"""Handles the logic of the core application, especially HTTP requests and access to different manager classes."""
#Importing necessary modules and classes from the Flask web framework
from flask import Flask, jsonify, request, make_response
#Importing the various managers
from packages.token_manager import TokenManager
from packages.data_manager import DataManager
from packages.robot_logic_manager import RobotLogicManager
#Importing signal to handle events
import signal
#Importing command classes
from packages.plugins.utils.commands import *
#For Widget functionality
from PyQt5.QtCore import QThread, pyqtSignal
#Shutdown
import os
#Token extraction from client input
import json

#Server class
class Server(QThread):

    #Creating signals for the widget

    #For updating the client counter with the current count
    counter_signal = pyqtSignal(int)

    #For manipulating the client table
    #Dict: Data like token, plugin, command and parameters
    #Bool1: Adding(0) or removing data (1)
    #Bool2: Creating a new line (0) or updating a row (1)
    table_signal = pyqtSignal(dict, bool, bool)

    #For creating messages about clients
    #Str1: Token
    #Str2: Mode (LOGIN, LOGOUT)
    user_info_signal =pyqtSignal(str, str)

    #For creating a login notification
    login_signal = pyqtSignal()

    #For server control
    start_signal = pyqtSignal()

    #Sending the URL to the widget
    url_signal = pyqtSignal(str)

    def __init__(self):

        #For threading
        super().__init__()

        #Updating widget count
        self.client_count = 0
        self.counter_signal.emit(self.client_count)

        #Create a Flask app
        self.app = Flask(__name__)

        #Creating instances of the managers
        self.tm = TokenManager()
        self.dm = DataManager()
        self.rlm = RobotLogicManager()

        #Register the shutdown function for SIGINT (Ctrl + C)
        #Allows manual shutdown in the terminal
        signal.signal(signal.SIGINT, self.manual_shutdown)

        #The following sections defines the handling of incoming http requests
        #Token_json is a json formatted string including the token, which serves as an identifier
        #For more details on the individual commands please check GitHub or the accompanying thesis

        #REST-API: POST /login 200 {}
        #Login response: Generated token is sent to client
        @self.app.route("/login", methods=["POST"])
        def login_response():

            #Login notification in GUI
            self.login_signal.emit()

            #Start of refined plugin loading proces
            self.available_plugins = dict(self.rlm.get_discovery())
            #Selecting plugin through user input in the terminal
            path = self.select_plugin(self.available_plugins)

            #Dynamically load and register the plugin
            plugin_name = self.rlm.load_module(path)

            #Generating and preparing the token for messaging
            generated_token = self.tm.generate_token()
            data = {
                "token" : generated_token
            }

            #Saving the combination of token and plugin name -> REST statelessness
            self.dm.save_plugin(generated_token, plugin_name)

            #Getting starting state of the application
            instance = self.rlm.create_instance(plugin_name)
            app_state = instance.setup()
            #Saving starting state of the application
            self.dm.save_state(generated_token, app_state)

            #Saving an SEND command as the starting command of the client
            base_command = CommandSEND()
            self.dm.save_command(generated_token, base_command)

            #UI updates

            #Update client count
            self.client_count += 1
            self.counter_signal.emit(self.client_count)

            #Updating client table
            table_info = dict(data)
            #Plugin name without telepath_ prefix and .py suffix
            plugin_without_prefix = plugin_name[9:-3]
            table_info["plugin_name"] = plugin_without_prefix
            self.table_signal.emit(table_info, False, False)

            #Sending status update to GUI
            self.user_info_signal.emit(generated_token, "LOGIN")

            #Sending the token to the client
            response = make_response(jsonify(data))
            response.headers['Cache-Control'] = 'no-cache'

            print("Login successful.")
            return response, 200
    
            
        #REST-API: GET /newcommand/<token> 200 {}
        #Response to command request: parameters object must be sent back
        @self.app.route("/newcommand/<token_json>", methods=["GET"])
        def command_response(token_json: str):

            #Extract token from JSON
            token = self.extract_token(token_json)

            #Check token authenticity
            if self.tm.check_token_authenticity(token):

                #Get generated commmand from MongoDB
                command = self.dm.retrieve_command(token)

                #Update widget
                table_info = dict(command)
                table_info["token"] = token
                self.table_signal.emit(table_info, False, True)

                #Response construction

                #For larger data packages make_response is recommended
                #Since just returning jsonify(data package) might lead to data loss during transmission
                response = make_response(jsonify(command))
                response.headers['Cache-Control'] = 'no-cache'

                print("Command sent.")
                return response, 200
            
            else:
                print("Error: No valid token provided for command reception.")
                #Response creation
                response = make_response("")
                    
                return response, 401 #Unauthorized


        #REST-API: POST /newcommand/<token> 200 {}
        #Response to command confirmation: no return object
        #Generates a command and stores it in MongoDB
        @self.app.route("/newcommand/<token_json>", methods=["POST"])
        def command_confirmation(token_json: str):
            
            #Extract token from JSON
            token = self.extract_token(token_json)

            #Check token authenticity
            if self.tm.check_token_authenticity(token):

                #Gets the app state, plugin_name and last command from MongoDB
                #State is a dict
                state = self.dm.retrieve_state(token)
                plugin_name = self.dm.retrieve_plugin(token)
                last_cmd = self.dm.retrieve_command(token)

                #Checks, whether this was an EXIT command
                if last_cmd["command"] == "EXIT":
                    #If it is an EXIT command, the logout sequence is activated
                    #No new command is generated
                    self.logout(token, plugin_name)
                    print("EXIT command confirmed. Client logged out.")

                #Otherwise a new command is generated by the system
                else:
                    #Grab ID from MongoDB
                    plugin_name = self.dm.retrieve_plugin(token)
                    #Grab plugin instance
                    instance = self.rlm.create_instance(plugin_name) 
                        
                    #Run the plugin and return the output -> command object, state dict
                    #Pass application state as argument
                    command, app_state = instance.run(state)

                    #Save the app state and command
                    #Should be function in DM
                    self.dm.save_state(token, app_state)
                    self.dm.save_command(token, command)

                    print("Command confirmed. Next command generated.")

                #Response creation
                response = make_response("")

                return response, 200
            
            else:
                print("Error: No valid token provided for command confirmation.")
                #Response creation
                response = make_response("")
                    
                return response, 401 #Unauthorized


        #REST-API: PUT /safeinfo/<token> 200 {"msg" : String}
        #Response to info file from client: file is saved in database
        @self.app.route("/saveinfo/<token_json>", methods=["PUT"])
        def saveinfo_response(token_json: str):

            #Extract token from JSON
            token = self.extract_token(token_json)

            #Check token authenticity and media type
            if self.tm.check_token_authenticity(token) and request.content_type == "application/json":
                data = request.get_json()
                data["token"] = token
                self.dm.save_data("infos", data)

                print("Info saved.")

                #Response creation
                response = make_response("")

                return response, 200
            
            else:
                print("Error: Check token validity and ensure content type JSON.")
                #Response creation
                response = make_response("")
                    
                return response, 401 #Unauthorized

        #REST-API: POST /safelog/<token> 200 {"filename" : String, "data" : String}
        #Response to log file from client: file is saved in database
        @self.app.route("/savelog/<token_json>", methods=["POST"])
        def savelog_response(token_json: str):

            #Extract token from JSON
            token = self.extract_token(token_json)

            #Check token authenticity and media type
            if self.tm.check_token_authenticity(token) and request.content_type == "application/json":
                data = request.get_json()
                data["token"] = token
                self.dm.save_data("logs", data)

                print("Log file saved.")

                #Response creation
                response = make_response("")

                return response, 200
            
            else:
                print("Error: Check token validity and ensure content type JSON.")
                #Response creation
                response = make_response("")
                    
                return response, 401 #Unauthorized
            
        #Not defined in the REST-API
        #For server shutdown through GUI
        @self.app.route("/shutdown", methods = ["POST"])
        def shutdown():
            
            self.shutdown_server()

            response = make_response(jsonify({"succes": True}))

            return response, 200
        
    #Methods for server handling

    #Starts the server and returns the base url
    def run(self):

        #GUI signal to notify user about start
        self.start_signal.emit()

        #Start the Flask server
        #According to the client side API implementation

        #The robot will attempt a connection to serverurl = "http://172.31.1.100:3000/"
        my_host = "172.31.1.100"
        my_port = 3000

        #For development outside of the lab run:
        # my_host = "127.0.0.1"
        # my_port = 3000

        #Return the base url to automatically setup the widget
        base_url = "http://" + my_host + ":" + str(my_port) + "/"
        self.url_signal.emit(base_url)

        #Start the server
        self.app.run(host= my_host, port= my_port)
                            
    #Shutting down server
    def shutdown_server(self):

        #Stopping MongoDB
        self.dm.stop_mongodb()

        #Kill python process
        #This will end all threads
        os.kill(os.getpid(), signal.SIGINT)

    #Defines the behaviour during server shutdown in the terminal
    def manual_shutdown(self, sig, frame):
        print("Shutting down server gracefully...")
        #Stopping MongoDB
        self.dm.stop_mongodb()
        print("Server shut down")
        exit(0)

    #Handling client logout
    def logout(self, token: str, plugin_name: str):

        #Reduce client count
        self.client_count -= 1
        #Update widget
        self.counter_signal.emit(self.client_count)

        #Removing token from TokenManager
        self.tm.delete_token(token)

        #Removing relevant data from MongoDB: no errors, if an identical token is generated
        self.dm.delete_data(token)

        #Update widget
        table_info = {"token": token}
        self.table_signal.emit(table_info, True, False)
        self.user_info_signal.emit(token, "LOGOUT")

    #The token is send by the client in JSON format:
    #e.g. {"token": "ABCD1234}
    #This method helps to extract the token
    def extract_token(self, json_input: dict):
        
        data = json.loads(json_input)
        token = data["token"]

        return token

    #Allows plugin choice in the terminal
    def select_plugin(self, plugin_selection: dict):
        print("New client attempts to login!")
        print("Available plugins for robot logic:")
        
        #Print a list of plugins
        for element in plugin_selection.keys():
            print("\t"+str(element))

        user_input = input("Please select a plugin by name: ")

        allowed_input = False
        while allowed_input == False:
            try:
                path = self.available_plugins[user_input]
            except KeyError:
                user_input = input("Plugin not found. Please try again: ")
            else:
                allowed_input = True
                print("Plugin selection succesful.")
        
        return path