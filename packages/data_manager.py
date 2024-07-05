"""This file handles operations revolving around the MongoDB database"""
#Pymongo is a Python driver for MongoDB
import pymongo
#Additional imports allow to run scripts 
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
        self.db = self.client["test"]

        collections_list = ["positions", "logs", "infos"]

        #Inserts collections with base entry if necessary
        for collection in collections_list:
            if collection not in self.db.list_collection_names():
                new_col = self.db[collection]
                if collection == "positons":
                    dict = {"token" : "", "X": 0, "Y": 0, "Z": 0, "A": 0, "B": 0, "Z": 0}
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
        mongodb_bin_path = os.path.join(dir_path, '../mongodb/macos/bin/mongod')
        db_path = os.path.join(dir_path, '../data')
        log_path = os.path.join(dir_path, '../logs/mongodb.log')

        # Ensure paths exist
        os.makedirs(db_path, exist_ok=True)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # Start MongoDB process
        process = subprocess.Popen(
            [mongodb_bin_path, '--dbpath', db_path, '--logpath', log_path, '--fork'],
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
        mongodb_bin_path = os.path.join(dir_path, '../mongodb/macos/bin/mongod')

        # Find MongoDB process ID and stop it
        try:
            result = subprocess.run(['pgrep', '-f', mongodb_bin_path], stdout=subprocess.PIPE)
            pid = int(result.stdout.strip())

            if pid:
                subprocess.run(['kill', str(pid)])
                print(f"MongoDB process {pid} stopped successfully.")
            else:
                print("MongoDB process not found.")
        except Exception as e:
            print(f"Error stopping MongoDB: {str(e)}")

    #saves data in the dictionary
    def save_data(self, dict, collection):
        pass
    
    #returns the requested document
    def query_data(self, query):
        pass
    

dm = DataManager()
dm.stop_mongodb()