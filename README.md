
Telepath RemoteMind - A framework for the server-based control of industrial robots utilizing a REST-API

_________________________________________

Contents:
1. Introduction
2. Overview
3. Installation Guide
4. User Guide
5. Plug-In Development
6. Known Issues

_________________________________________

1. Introduction

    Industrial robots have become an increasingly important part of production systems across industries over past decades.
   Robot programming is typically done offline using a proprietary programming languague or online directly in the robot cell over a programming device.
   In both cases programs are saved on the robot controller and accessed during operations.

    Decoupling the robot hardware from proprietary software systems can open up a new dimension of possibilities. This is especially a topic of interest considering the rise of artificial intelligence applications. These might be limited by the restrictions concerning the controller like computing power.

    Therefore, a previous thesis resulted in the development of a REST-API running in Java on the Kuka LBR iiwa cobot in the laboratory of production technology at Technische Hochschule Ingolstadt. This alllows the robot controller to take on the role of a client connecting to a server, which can in turn feed it with a set of commands determined by arbitrary control or planning systems. My thesis is focusing on the development of such a AI server. While the architecture and design of the application are discussed in-depth in the thesis, this repository represents the practical implementation of these considerations.

    NOTE: A client implementation is not included in this project and is significantly influenced by the supplier's hardware and software design.

_________________________________________

2. Overview

    The application is built around a core system handling client-server-communication. This core integrates into a plug-in architecture, which allows for the dynamic loading of logic modules during runtime.
    These modules generate commands for the robot and must adhere to a plug-in interface in order to function properly, which is demonstrated by some examples provided in the repository. Python has been chosen as the programming languague for implementation and will hopefully serve well in the development of further plugins as the leading language the machine learning space.

    The core application is found under "packages" and includes the following components:

        - Server: A Flask server calling on other modules to facilitate client-server communication in accordance with the REST-API specification and design principals
        - TokenManager: Generates and stores tokens used for client verification
        - DataManager: Allows for access to a MongoDB database to store information
        - RobotLogicManager: The plug-in manager discovers and loads plug-ins during runtime
        - Widget: A compact Qt5 UI displaying info about current clients and offering some basic server control

    The plug-in architecture requires additional components found under "packages/plugins/utils":

        - PluginInterface: The interface all plug-ins must adhere to
        - Commands: Actually a collection of classes, which help to create properly formatted robot commands
        - MongoInterface: Allows to connect plug-ins to the running MongoDB instance if necessary

    Additionally, some example plug-ins are offered:

        Demos:
            - Telepath Commands: Runs all six robot commands once by utilizing a counter. Effectively demonstrates the ability to program the robot in Python
            - Telepath Skilltree: Utilizing an ontology, this plug-in simulates unlocking new robot abilities by using a level counter
            - Telepath Sync: Demonstrates a way to control two robots with the same base code

        Telepath Blueprints - a ontology based approach to dynamic robot control:
            This plugin relies on a ontology modeling products, their individual parts, assembly instructions for each part and the necessary assembly actions. By querying the relations between these elements it is able to determine a correct course of action. This might be especially interesting for large and complex processes, since the initial time investment is offset by having a system dynamically adapting to changes in assembly conditions, which is not seen in linear and static robot programs. The plug-in offers two example products, a drawing of a house and a stickman.

_________________________________________

3. Installation Guide

    Pre-requisites:
        -  A MacOS or Windows device
        -  Python
        -  Git
        -  An IDE (e.g. VS Code)

    Follow these steps and enter the commands in your terminal - always ensure the correct directory and an active virtual environment:

        1. Create a project folder
        2. Create a virtual environment to isolate dependencies in this folder: python3 -m venv venv (MAC) or python -m venv venv (WIN)
        3. Activate the virtual environment: source venv/bin/activate (MAC) or venv\Scripts\activate (WIN)
        4. Clone the repository: Recommended to use VS Code's command palette at the top by entering  ">git: clone" and adding the repository url found on GitHub under the green "Code" button
        5. Install the requirements: pip install -r requirements.txt (WIN/MAC) (If PyQt5 is causing troubles, try installing it separately: pip install PyQt5)
        6. Create the following folder structure in the same directory as main.py:  mongodb/
                                                                                        │
                                                                                        ├── data/
                                                                                        │
                                                                                        ├── logs/
                                                                                        │
                                                                                        └── bin/
                                                                                            ├── macOS/
                                                                                            └── windows/
        7. Download the MongoDB Community Server from the website - make sure to select the correct OS: https://www.mongodb.com/try/download/community-kubernetes-operator
        8. Unpack the bin files and add them to the corresponding directory you just created
        
        Additional recommendations:
            - Download Postman to test the server and your plug-ins: https://www.postman.com
            - Change the server host: The software is set-up to connect to the lab cobot. Instead comment out line 303 and 304 in the run() function of server and use line 307 and 308.
            - Check the Known Issues section

_________________________________________

4. User Guide

    Currently a hybrid approach to user control is utilized, combining the terminal and a GUI

    The application is started by executing main.py, which will in turn display the GUI widget.
    The widget offers basic controls and displays information:
        - Start Button: Starts the Flask server and in turn MongoDB
        - Stop Button: Stops MongoDB and shuts the app down, including the GUI. Requires a confirmation dialog to do so
        - Client Counter: Shows the number of connected robots
        - Status line: Displays some basic info on the server status and will urge the user to check the terminal
        - Client table: An overview of clients including their identification token, the selected plug-in, their last command and its parameters

    The terminal is used to select options. For example the user is prompted to select a plug-in during each login. To avoid confusion the status bar will signal the login attempt.
    Some plugins also use the terminal for user input mostly during set-up.

_________________________________________

5. Plug-In Development

    This is a short overview of key mechanisms for plug-in development. For detailled information please refer to the master's thesis

    A client should communicate in the following fashion:
        1. Login
        2. Loop until an Exit command is sent by the server:
            1. Get a new command
            2. Confirm the command - this is the sign for the server to generate the next command
            3. Execute the command
        3. End the program
    
    The server will thus mirror the client behaviour to ensure functionality of the whole system.
    It is important to understand that the core application cannot create commands - this is entirely up to the plugins.

    Plug-Ins adhere to the interface by implementing the following methods:
        - The constructor __init__(): Called during every instantiation of the plug-in
        - setup(): 
            A method called during client login to generate the inital state of the application.
            Returns a state
        - run(state: dict): 
            The core method of the application, similar to a main.py file this is used during the command confimation to execute the app logic and generate a new command
            Takes in a state
            Returns a command and a state
   
   It is important to understand that a plug-in can consist of several modules.
   However, it is necessary to have a main file, which only includes one class serving as the proper implementation of the interface.
   This file must be named with the "telepath_" prefix in mind, in order to allow discovery by the robot logic manager.
   Place the application somewhere inside the "plugin" directory or a subdirectory inside.

    What is a command?
        Commands include all information necessary for the robot to execute certain pre-defined behaviour
        This includes
            - LIN: linear movement, shortest path
            - PTP: fastest movement, not linear
            - CIRC: circular movement
            - SEND: get some robot info
            - LOG: get robot log files
            - EXIT: exit the request loop and end program execution
        
        Movement require frames: point or coordinate systems in the workspace defined by their position (X, Y, Z) and rotation (A, B, C) relative to the robot's world coordinate system
        Please always use the included command classes to generate these commands

    What is a state?
        A state describes all variables of an application that allow it to resume seemless execution despite repeated instantiation.
        It takes the form of a Python dictionary.

        This variable is a result of the REST principle of statelessness: The server cannot save a state or client information in-between requests
        To adhere to these constraints a plug-in instance exists only for the duration of a single method call
        Therefore the state variable as well as MongoDB are used to recreate the necessary state

        State is probably best demonstrated by an example:
            Telepath Commands uses a counter to switch between methods. 
            Since the plug-in is always newly instantiated during an API call it is not possible to just add +1 to the counter after every call.
            Instead the setup() function creates a initial state = {"counter": 1} and passes it back to the Server into MongoDB.
            During a new command generation the state is passed into the run() function, which uses it to select the next command
            At the end the counter is updated to state = {"counter": 2} and once again returned to the Server.
            This process repeats itself until the plug-in sends an EXIT command at counter = 6, prompting the client to log out.

    Outside of these constraints the possibilities of plug-in development are virtually limitless. 
    Even the design of the state variable is completely up to the developer, as long as compatibility with MongoDBs document based approach to storage is ensured.

_________________________________________

6. Known Issues

    After finishing a complete run of Telepath Blueprints until completion the application will cause an Index Error, if the same plug-in is selected for a new client. 
    Restarting the app and running Blueprints does not cause any issues.

    The GUI might appear distorted on some machines.

    On Windows the GUI will become unresponsive after pressing start initially. Terminating execution and retrying will allow the app to work properly, since MongoDB should now already run in the background. This is probably due to difference in MongoDB's start-up behaviour between Windows and Mac. Such an issue does not occur on Mac and makes it the recommended platform at the moment.

    PyQt5 causes issues during the creation of a Docker container. Since the server will be mainly used for the development of plug-ins and experimentation in the lab, running the code natively is recommended.
    Otherwise removing the widget and making changes to the server and main.py will mirror earlier development stages and is the recommended approach for containerization.
            
