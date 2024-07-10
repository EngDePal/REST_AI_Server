"""Handles the logic of the core application, especially HTTP requests and access to different manager classes."""
#Importing necessary modules and classes from the Flask web framework
from flask import Flask, jsonify, request
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

#For testing
module = 0

#The following sections defines the handling of incoming http requests
#Token variable in most URI serves the identficiation of different clients
#For more details on the individual commands please check GitHub or the accompanying thesis

#REST-API: POST /login 200 {}
#Login response: Generated token is sent to client
@app.route("/login", methods=["POST"])
def login_response():

    #During login a decision about the necessary plugin instance must be made
    #For testing purposes we will load one module
    global module
    path = "/Users/dennispal00/Documents/Masterarbeit_THI/REST_AI_Server/packages/plugins/barebones_plugin.py"
    module = rlm.load_module(path)
    
    #Generating and sending the token
    data = {
        "token" : tm.generate_token()
    }
    return jsonify(data), 200
    
#REST-API: GET /newcommand/<token> 200 {}
#Response to command request: parameters object must be sent back
@app.route("/newcommand/<token>", methods=["GET"])
def command_response(token):
    #This must be quite a bit more complex
    #The correct plugin instance should be called according to a mapping token:plugin
    #For testing purposes, our barebones_plugin will suffice
    #Subject to change
    global module
    data = module.run()

    return jsonify(data), 200


#REST-API: POST /newcommand/<token> 200 {}
#Response to command confirmation: no return object, server can generate the next command
@app.route("/newcommand/<token>", methods=["POST"])
def command_confirmation(token):
    #Still not sure, what to do here: probably overwrite the last command with the new command in MongoDB
    #Collection 'robot_status'
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

