"""Handles the logic of the core application, especially HTTP requests and access to different manager classes"""
#Importing necessary modules and classes from the Flask web framework
from flask import Flask, request, jsonify
#Importing the various managers
from token_manager import TokenManager

#Create a flask app
app = Flask(__name__)

#Creating instances of the managers
tm = TokenManager()


#The following sections defines the handling of incoming http requests
#Token variable in most URI serves the identficiation of different clients
#For more details on the individual commands please check GitHub or the accompanying thesis

#Login response: Generated token is sent to client
@app.route('/login', methods=['POST'])
def login_response():
    data = {
        "token" : tm.generate_token()
    }
    return jsonify(data)
    

#Response to command request: parameters object must be sent back
@app.route('/newcommand/<token>', methods=['GET'])
def command_response(token):
    pass

#Response to command confirmation: no return object, server can generate the next command
@app.route('/newcommand/<token>', methods=['POST'])
def command_confirmation(token):
    pass

#Response to info file from client: file is saved in database
@app.route('/safeinfo/<token>', methods=['POST'])
def safeinfo_response(token):
    pass

#Response to log file from client: file is saved in database
@app.route('/safelog/<token>', methods=['POST'])
def safelog_response(token):
    pass

if __name__ == "__main__":
    app.run()
