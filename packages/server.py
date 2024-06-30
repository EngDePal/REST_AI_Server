"""Handles the logic of the core application, especially HTTP requests and access to different manager classes"""
#Importing necessary modules and classes from the Flask web framework
from flask import Flask, request, jsonify

#Create a flask app
app = Flask(__name__)

#The following sections defines the handling of incoming http requests
#For more details on the individual commands please check GitHub or the accompanying thesis


@app.route('/<test>')
def home(test):
    return f"Hello, {test}!"
