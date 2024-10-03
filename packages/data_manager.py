"""Handles operations involving the MongoDB database."""
#Pymongo is a Python driver for MongoDB
import pymongo
#Additional imports allow to start mongodb 
import subprocess
import os
#For OS check
import platform
#Cross platform comptibility
import psutil

class DataManager:

    #Constructor starts and set-ups database
    def __init__(self):
        self.start_mongodb()
        self.setup()

    #Initializes the database and collections with basic dictionaries
    def setup(self):

        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        
        #Loads or creates database if necessary
        self.db = self.client["REST_AI_Server"]

        self.collections_list = ["app_state", "logs", "infos", "plugins", "commands"]

        #Remove temporary data first, in case there was no proper shutdown
        for collection in ["app_state", "plugins", "commands"]:
            target_collection = self.db[collection]
            target_collection.delete_many({})

        #Inserts collections with base entry, if necessary
        #View these as examples or formats 
        #Except for app state, which depends on the plugin
        for collection in self.collections_list:
            if collection not in self.db.list_collection_names():
                new_col = self.db[collection]
                #State restores app state of plugins -> RESTful
                if collection == "app_state":
                    #This is only an example of the robot coordinates as the state
                    #Properties of the state file are determined by the plugin
                    db_file = {"token" : "",
                            "command" : "", 
                            "parameters": {
                                "type": "",
                                "frame": {
                                    "X": 0, 
                                    "Y": 0, 
                                    "Z": 0, 
                                    "A": 0, 
                                    "B": 0, 
                                    "Z": 0}
                            }
                    }
                #Log files of client
                elif collection == "logs":
                    db_file = {"token" : "", "filename": "", "data": ""}
                #Info files of client
                elif collection == "infos":
                    db_file = {"token" : "", "msg": ""}
                #Plugin selection of clients
                elif collection == "plugins":
                    db_file = {"token": "", "plugin_name": ""}
                #Saving generated command
                elif collection == "commands":
                     db_file = {"token" : "",
                            "command" : "", 
                            "parameters": {
                                "type": "",
                                "frame": {
                                    "X": 0, 
                                    "Y": 0, 
                                    "Z": 0, 
                                    "A": 0, 
                                    "B": 0, 
                                    "Z": 0}
                            }
                    }
                base_entry = new_col.insert_one(db_file)
                
        print("Database is set-up!")
    
    #Starts the MongoDB process accroding to OS expectation
    def start_mongodb(self):
        
        #Define paths
        dir_path = os.path.dirname(os.path.realpath(__file__))

        if platform.system() == "Darwin" or platform.system() == "Linux":
            mongodb_bin_path = os.path.join(dir_path, "../mongodb/bin/macos/mongod")
        elif platform.system() == "Windows":
            mongodb_bin_path = os.path.join(dir_path, "../mongodb/bin/windows/mongod.exe")
        else:
            raise Exception("Unknown operating system. No MongoDB binaries available.")
        db_path = os.path.join(dir_path, "../mongodb/data")
        log_path = os.path.join(dir_path, "../mongodb/logs/mongodb.log")

        #Ensure paths exist
        os.makedirs(db_path, exist_ok=True)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        #Start MongoDB process
        #Darwin is MacOS
        if platform.system() == "Darwin" or platform.system() == "Linux":
            process = subprocess.Popen(
                [mongodb_bin_path, "--dbpath", db_path, "--logpath", log_path, "--fork"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        #Windows takes longer to start MongoDB, leading to a freezing GUI
        #Stop code execution and restart, which should allow the server to work as intendede
        elif platform.system() == "Windows":
            process = subprocess.Popen(
                [mongodb_bin_path, "--dbpath", db_path, "--logpath", log_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            raise Exception("Unknown operating system. No MongoDB binaries available.")

        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print("MongoDB started successfully.")
        else:
            print(f"Error starting MongoDB: {stderr.decode()}")    

    #Stops MongoDB
    def stop_mongodb(self):

        #Define paths
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if platform.system() == "Darwin" or platform.system() == "Linux":
            mongodb_bin_path = os.path.join(dir_path, "../mongodb/bin/macos/mongod")
        elif platform.system() == "Windows":
            mongodb_bin_path = os.path.join(dir_path, "../mongodb/bin/windows/mongod.exe")
        else:
            raise Exception("Unknown operating system. No MongoDB binaries available.")

        #Find MongoDB process ID and stop it
        try:

            if platform.system() == "Darwin" or platform.system() == "Linux":
                result = subprocess.run(["pgrep", "-f", mongodb_bin_path], stdout=subprocess.PIPE)
                pid = int(result.stdout.strip())

                if pid:
                    subprocess.run(['kill', str(pid)])
                    print(f"MongoDB process {pid} stopped successfully.")
                else:
                    print("MongoDB process not found.")
            
            elif platform.system() == "Windows":
                #Using psutil on Windows to find and terminate the process
                for proc in psutil.process_iter(['pid', 'name']):
                    if "mongod.exe" in proc.info['name']:
                        proc.terminate()  #Send termination signal
                        proc.wait()  #Wait until the process is terminated
                        print(f"MongoDB process {proc.info['pid']} stopped successfully.")
                        break
                else:
                    print("MongoDB process not found.")

        except Exception as e:
            print(f"Error stopping MongoDB: {str(e)}")

    #Saves the dictionary in the specified collection
    def save_data(self, collection: str, db_file: dict):
        if collection in self.collections_list:
            chosen_collection = self.db[collection]

            #Regarding app_state: In order to avoid complex queries and 
            #Ensure the return of only the latest state, prior entries will be deleted
            if collection == "app_state":
                token = db_file["token"]
                doc = self.query_data("app_state", {"token": token})
                #Checks for previous entries, deletes them
                if len(doc) != 0:
                    chosen_collection.delete_many({"token": token})

            #Regarding commands: In order to avoid complex queries and 
            #Ensure the return of only the latest state, prior entries will be deleted
            if collection == "commands":
                token = db_file["token"]
                doc = self.query_data("commands", {"token": token})
                #Checks for previous entries, deletes them
                if len(doc) != 0:
                    chosen_collection.delete_many({"token": token})

            #Regarding infos: In order to keep the PUT methode idempotent, prior entries will be deleted
            if collection == "infos":
                token = db_file["token"]
                doc = self.query_data("infos", {"token": token})
                #Checks for previous entries, deletes them
                if len(doc) != 0:
                    chosen_collection.delete_many({"token": token})

            chosen_collection.insert_one(db_file)
    
    #Save functions to shorten server code

    def save_plugin(self, token: str, plugin_name:str):
        db_file = {"token" : token, "plugin_name": plugin_name}
        self.save_data("plugins", db_file)

    def save_state(self, token: str, state: dict):
        db_file = state
        db_file["token"] = token
        self.save_data("app_state", db_file)

    def save_command(self, token: str, command:dict):
        db_file = command
        db_file["token"] = token
        self.save_data("commands", db_file)
    
    #Returns a list of the requested documents after taking in a query dictionary
    #So far only used for database testing
    #Empty dict will return the whole collection
    def query_data(self, collection: str, query_dict: dict):
        if collection in self.collections_list:
            chosen_collection = self.db[collection]
            #Returns a cursor object and turns it into a list of dictionaries
            document = list(chosen_collection.find(query_dict))
            return document
    
    #Get plugin name from server
    #Does not need a query dict as an argument
    #Shortens server code
    def retrieve_plugin(self, token: str):
        #Get the fitting document from MongoDB
        try:
            query = {"token" : token}
            result = self.query_data("plugins", query)
            doc = result[0]
            #Only returns the plugin name
            id = doc["plugin_name"]
            return id
        except IndexError:
            return 0
    
    #Retrieves the app_state
    def retrieve_state(self, token: str):
        #Get the fitting document from MongoDB
        try:
            query = {"token" : token}
            result = self.query_data("app_state", query)
            doc = result[0]
            doc.pop("_id")
            return doc
        except IndexError:
            return {}
        
    #Retrieves recent command
    def retrieve_command(self, token: str):
        #Get the fitting document from MongoDB
        try:
            query = {"token" : token}
            result = self.query_data("commands", query)
            doc = result[0]
            doc.pop("_id")
            doc.pop("token")
            return doc
        except IndexError:
            return {}

    #Deletes app state and plugins, if a client logs out
    def delete_data(self, token: str):

        parameters = {"token" : token}
        
        for collection in ["app_state", "plugins", "commands"]:
            target_collection = self.db[collection]
            target_collection.delete_many(parameters)

    #Drops the database
    #Allows for clean-up
    def delete_db(self, db_name: str):
        self.client.drop_database(db_name)
