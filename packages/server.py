"""Handles the logic of the core application, especially HTTP requests and access to different manager classes."""
#Importing necessary modules and classes from the Flask web framework
from flask import Flask, jsonify, request
#Importing the various managers
from token_manager import TokenManager
from data_manager import DataManager
#Importing signal to handle events
import signal

#Create a flask app
app = Flask(__name__)

#Creating instances of the managers
tm = TokenManager()
dm = DataManager()


#The following sections defines the handling of incoming http requests
#Token variable in most URI serves the identficiation of different clients
#For more details on the individual commands please check GitHub or the accompanying thesis

#Login response: Generated token is sent to client
@app.route("/login", methods=["POST"])
def login_response():
    data = {
        "token" : tm.generate_token()
    }
    return jsonify(data), 200
    

#Response to command request: parameters object must be sent back
@app.route("/newcommand/<token>", methods=["GET"])
def command_response(token):
    pass

#Response to command confirmation: no return object, server can generate the next command
@app.route("/newcommand/<token>", methods=["POST"])
def command_confirmation(token):
    pass

#Response to info file from client: file is saved in database
@app.route("/safeinfo/<token>", methods=["POST"])
def safeinfo_response(token):
    data = request.get_json()
    data["token"] = token
    dm.save_data("infos", data)
    return {}, 200

#Response to log file from client: file is saved in database
@app.route("/safelog/<token>", methods=["POST"])
def safelog_response(token):
    pass

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

