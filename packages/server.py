"""Handles the logic of the core application, especially HTTP requests and access to different manager classes."""
#Importing necessary modules and classes from the Flask web framework
from flask import Flask, jsonify, request
import json
#Importing the various managers
from token_manager import TokenManager
from data_manager import DataManager
from robot_logic_manager import RobotLogicManager
#Importing signal to handle events
import signal

#Create a flask app
app = Flask(__name__)

#Creating instances of the managers
tm = TokenManager()
dm = DataManager()
rlm = RobotLogicManager()

#The following sections defines the handling of incoming http requests
#Token variable in most URI serves the identficiation of different clients
#For more details on the individual commands please check GitHub or the accompanying thesis

#REST-API: POST /login 200 {}
#Login response: Generated token is sent to client
@app.route("/login", methods=["POST"])
def login_response():

    #Start of refined plugin loading proces
    #available_plugins = rlm.get_discovery()


    #During login a decision about the necessary plugin instance must be made
    #For testing purposes we will load one module
    path = "/Users/dennispal00/Documents/Masterarbeit_THI/REST_AI_Server/packages/plugins/prototypes/telepath_test.py"
    #Generate a new plugin_id
    plugin_id = tm.generate_id()
    #Dynamically load and register the plugin
    rlm.load_module(path, plugin_id)
    
    #Generating and preparing the token
    generated_token = tm.generate_token()
    data = {
        "token" : generated_token
    }

    #Saving the combination of token and plugin_id -> REST statelessness
    db_file = {"token" : generated_token, "plugin_id": plugin_id}
    dm.save_data("plugins", db_file)

    #Sending the token to the server
    return jsonify(data), 200
    
#REST-API: GET /newcommand/<token> 200 {}
#Response to command request: parameters object must be sent back
@app.route("/newcommand/<token>", methods=["GET"])
def command_response(token):
    #This must be quite a bit more complex
    #The correct plugin instance should be called according to a mapping token:plugin
    #For testing purposes, our barebones_plugin will suffice
    #Subject to change
    
    #Gets the robot status and plugin_id from MongoDB
    status = dm.retrieve_status(token)
    plugin_id = dm.retrieve_id(token)

    #For the first command there will be an empty list
    #Sets the confirmation to true in this case
    if status == {}:
        status["confirmation"] = True

    #Checks for confirmed command and authentic token
    if status["confirmation"]:
        if tm.check_token_authenticity(token):
            #Grab ID from MongoDB
            plugin_id = dm.retrieve_id(token)
            #Grab plugin instance
            instance = rlm.retrieve_plugin(plugin_id) 
            
            #Run the plugin and return the output -> command object
            command = instance.run()

            #Save the robot command
            db_file = dict(command)
            db_file["token"] = token
            db_file["confirmation"] = False
            dm.save_data("robot_status", db_file)

            return jsonify(command), 200


#REST-API: POST /newcommand/<token> 200 {}
#Response to command confirmation: no return object, server can generate the next command
@app.route("/newcommand/<token>", methods=["POST"])
def command_confirmation(token):

    #Changes confirmation on the recent command to True
    #Otherwise no new command will be generated in the next run
    dm.confirm_robot_command(token)

    return {}, 200

#REST-API: POST /safeinfo/<token> 200 {"msg" : String}
#Response to info file from client: file is saved in database
@app.route("/safeinfo/<token>", methods=["POST"])
def safeinfo_response(token):
    if tm.check_token_authenticity(token):
        data = request.get_json()
        data["token"] = token
        dm.save_data("infos", data)
        return {}, 200

#REST-API: POST /safelog/<token> 200 {"filename" : String, "data" : String}
#Response to log file from client: file is saved in database
@app.route("/safelog/<token>", methods=["POST"])
def safelog_response(token):
    if tm.check_token_authenticity(token):
        data = request.get_json()
        data["token"] = token
        dm.save_data("logs", data)
        return {}, 200

#Defines the behaviour during server shutdown in the terminal
def shutdown_server(sig, frame):
    print("Shutting down server gracefully...")
    #Stopping MongoDB
    dm.stop_mongodb()
    print("Server shut down")
    exit(0)

# Register the shutdown function for SIGINT (Ctrl + C)
signal.signal(signal.SIGINT, shutdown_server)

if __name__ == "__main__":
    app.run()

