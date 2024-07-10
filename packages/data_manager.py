"""Handles operations involving the MongoDB database."""
#Pymongo is a Python driver for MongoDB
import pymongo
#Additional imports allow to start mongodb 
import subprocess
import os

class DataManager:

    #Constructor starts and set-ups database
    def __init__(self):
        self.start_mongodb()
        self.setup()

    #Initializes the database and collections with basic dictionaries
    def setup(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        
        #Loads or creates database if necessary
        #Change this to 'REST_AI_Server' during deployment
        self.db = self.client["test"]

        self.collections_list = ["robot_status", "logs", "infos"]

        #Inserts collections with base entry if necessary
        for collection in self.collections_list:
            if collection not in self.db.list_collection_names():
                new_col = self.db[collection]
                if collection == "robot_status":
                    dict = {"token" : "", 
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
                    base_entry = new_col.insert_one(dict)
                elif collection == "logs":
                    dict = {"token" : "", "filename": "", "data": ""}
                    base_entry = new_col.insert_one(dict)
                elif collection == "infos":
                    dict = {"token" : "", "msg": ""}
                    base_entry = new_col.insert_one(dict)

        print("Database is set-up!")
    
    #Starts the mongod process
    def start_mongodb(self):
        # Define paths
        dir_path = os.path.dirname(os.path.realpath(__file__))
        mongodb_bin_path = os.path.join(dir_path, "../mongodb/macos/bin/mongod")
        db_path = os.path.join(dir_path, "../mongodb/data")
        log_path = os.path.join(dir_path, "../mongodb/logs/mongodb.log")

        # Ensure paths exist
        os.makedirs(db_path, exist_ok=True)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # Start MongoDB process
        process = subprocess.Popen(
            [mongodb_bin_path, "--dbpath", db_path, "--logpath", log_path, "--fork"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print("MongoDB started successfully.")
        else:
            print(f"Error starting MongoDB: {stderr.decode()}")    

    #Stops mongod
    def stop_mongodb(self):
        # Define paths
        dir_path = os.path.dirname(os.path.realpath(__file__))
        mongodb_bin_path = os.path.join(dir_path, "../mongodb/macos/bin/mongod")

        # Find MongoDB process ID and stop it
        try:
            result = subprocess.run(["pgrep", "-f", mongodb_bin_path], stdout=subprocess.PIPE)
            pid = int(result.stdout.strip())

            if pid:
                subprocess.run(['kill', str(pid)])
                print(f"MongoDB process {pid} stopped successfully.")
            else:
                print("MongoDB process not found.")
        except Exception as e:
            print(f"Error stopping MongoDB: {str(e)}")

    #Saves the dictionary in the specified collection
    def save_data(self, collection, dict:dict):
        chosen_collection = self.db[collection]

        #Regarding robot_status: In order to avoid complex queries and ensure the return of only the latest position, prior entries will be deleted
        if collection == "robot_status":
            token = dict["token"]
            doc = self.query_data("robot_status", {"token": token})
            if len(doc) != 0:
                chosen_collection.delete_many({"token": token})
        entry = chosen_collection.insert_one(dict)
    
    #Returns a list of the requested documents after taking in a query dictionary
    def query_data(self, collection, query_dict):
        if collection in self.collections_list:
            chosen_collection = self.db[collection]
            #Returns a cursor object and turns it into a list of dictionaries
            document = list(chosen_collection.find(query_dict))
            return document

    