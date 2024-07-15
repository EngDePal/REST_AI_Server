"""Handles the logic of the core application, especially HTTP requests and access to different manager classes."""
#Importing necessary modules and classes from the Flask web framework
from flask import Flask, jsonify, request
#Importing the various managers
from token_manager import TokenManager
from data_manager import DataManager
from robot_logic_manager import RobotLogicManager
#Importing signal to handle events
import signal


#Server class
class Server:

    def __init__(self):
        #Create a Flask app
        self.app = Flask(__name__)

        #Creating instances of the managers
        self.tm = TokenManager()
        self.dm = DataManager()
        self.rlm = RobotLogicManager()

        #Variables for data transmission to frontend
        self.available_plugins = dict()
        self.client_count = 0

        # Register the shutdown function for SIGINT (Ctrl + C)
        #Allows manual shutdown in the terminal
        signal.signal(signal.SIGINT, self.manual_shutdown)

        #The following sections defines the handling of incoming http requests
        #Token variable in most URI serves the identficiation of different clients
        #For more details on the individual commands please check GitHub or the accompanying thesis

        #REST-API: POST /login 200 {}
        #Login response: Generated token is sent to client
        @self.app.route("/login", methods=["POST"])
        def login_response():

            #Start of refined plugin loading proces
            self.available_plugins = dict(self.rlm.get_discovery())
            #UI not yet operational, this is done in the terminal
            path = self.classic_plugin_selection(self.available_plugins)

            #Generate a new plugin_id
            plugin_id = self.tm.generate_id()
            #Dynamically load and register the plugin
            self.rlm.load_module(path, plugin_id)
            
            #Generating and preparing the token
            generated_token = self.tm.generate_token()
            data = {
                "token" : generated_token
            }

            #Saving the combination of token and plugin_id -> REST statelessness
            db_file = {"token" : generated_token, "plugin_id": plugin_id}
            self.dm.save_data("plugins", db_file)

            #Update client count
            self.client_count += 1

            #Sending the token to the server
            print("Login successful.")
            return jsonify(data), 200
    
            
        #REST-API: GET /newcommand/<token> 200 {}
        #Response to command request: parameters object must be sent back
        @self.app.route("/newcommand/<token>", methods=["GET"])
        def command_response(token: str):
            
            #Gets the robot status and plugin_id from MongoDB
            status = self.dm.retrieve_status(token)
            plugin_id = self.dm.retrieve_id(token)

            #For the first command there will be an empty list
            #Sets the confirmation to true in this case
            if status == {}:
                status["confirmation"] = True

            #Checks for confirmed command and authentic token
            if status["confirmation"]:
                if self.tm.check_token_authenticity(token):
                    #Grab ID from MongoDB
                    plugin_id = self.dm.retrieve_id(token)
                    #Grab plugin instance
                    instance = self.rlm.retrieve_plugin(plugin_id) 
                    
                    #Run the plugin and return the output -> command object
                    #Pass robot status as argument
                    command = instance.run(status)

                    #Save the robot command
                    db_file = dict(command)
                    db_file["token"] = token
                    db_file["confirmation"] = False
                    self.dm.save_data("robot_status", db_file)

                    #Handling log-out
                    if command["command"] == "EXIT":
                        self.logout(token= token, plugin_id= plugin_id)


                    print("Command sent.")
                    return jsonify(command), 200
            else:
                return 500


        #REST-API: POST /newcommand/<token> 200 {}
        #Response to command confirmation: no return object, server can generate the next command
        @self.app.route("/newcommand/<token>", methods=["POST"])
        def command_confirmation(token: str):
            #Changes confirmation on the recent command to True
            #Otherwise no new command will be generated in the next run
            self.dm.confirm_robot_command(token)

            print("Command confirmed.")
            return jsonify({}), 200

        #REST-API: POST /safeinfo/<token> 200 {"msg" : String}
        #Response to info file from client: file is saved in database
        @self.app.route("/safeinfo/<token>", methods=["POST"])
        def safeinfo_response(token: str):
            if self.tm.check_token_authenticity(token):
                data = request.get_json()
                data["token"] = token
                self.dm.save_data("infos", data)

                print("Info saved.")
                return jsonify({}), 200

        #REST-API: POST /safelog/<token> 200 {"filename" : String, "data" : String}
        #Response to log file from client: file is saved in database
        @self.app.route("/safelog/<token>", methods=["POST"])
        def safelog_response(token: str):
            if self.tm.check_token_authenticity(token):
                data = request.get_json()
                data["token"] = token
                self.dm.save_data("logs", data)

                print("Log file saved.")
                return jsonify({}), 200
            
        
    #Methods for server handling

    #Starts the server
    def start_server(self):
        self.app.run()

    #Shutting down server
    #To be implemented
    def shutdown_server(self):
        pass

    #Defines the behaviour during server shutdown in the terminal
    def manual_shutdown(self, sig, frame):
        print("Shutting down server gracefully...")
        #Stopping MongoDB
        self.dm.stop_mongodb()
        print("Server shut down")
        exit(0)

    #Handling client logout
    def logout(self, token: str, plugin_id: str):

        #Reduce client count
        self.client_count -= 1

        #Removing token and ID from TokenManager
        self.tm.delete_token(token)
        self.tm.delete_id(plugin_id)

        #Removing plugin instance and name from RobotLogicManager
        self.rlm.remove_plugin(plugin_id= plugin_id)

        #Removing relevant data from MongoDB: no errors if identical token is regenerated
        self.dm.delete_data(token)

    #Allows plugin choice in the terminal
    #Should be kept in every case as legacy code
    def classic_plugin_selection(self, plugin_selection: dict):
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
        
        return path
    
server = Server()
server.start_server()