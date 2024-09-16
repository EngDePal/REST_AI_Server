"""This serves as an interface to MongoDB for Plug-Ins in need of data access"""
#Pymongo is a Python driver for MongoDB
import pymongo

class MongoInterface:

    #Connect to the running MongoDB instance
    def __init__(self):

        self.client = pymongo.MongoClient("mongodb://localhost:27017")

        self.db = self.client["REST_AI_Server"]

        #The standard server collections
        #Read only: Manipulation is not allowed and can impact the server
        self.collections_list = ["app_state", "logs", "infos", "plugins", "commands"]
    
    #Returns a list of the requested documents after taking in a query dictionary
    #So far only used for database testing
    #Empty dict will return the whole collection
    def query_data(self, collection: str, query_dict: dict):
        if collection in self.collections_list:
            chosen_collection = self.db[collection]
            #Returns a cursor object and turns it into a list of dictionaries
            document = list(chosen_collection.find(query_dict))
            return document
        
    #Saves the dictionary in the specified collection
    #If the collection does not exist yet, it will be created
    def save_data(self, collection: str, db_file: dict):
        
        if collection not in self.collections_list:
            chosen_collection = self.db[collection]

            chosen_collection.insert_one(db_file)

    #Deletes data based on the search parameteres
    def delete_data(self, collection: str, parameters: dict):
        
        if collection not in self.collections_list:
            collection.delete_many(parameters)

    #Deletes the specified collection
    def delete_collection(self, collection: str):
        if collection in self.db.list_collection_names():
            if collection not in self.collections_list:
                self.db[collection].drop()
                print(f"Collection {collection} has been deleted.")
            else:
                print(f"Deletion of selected collection {collection} not allowed.")
        else:
            print(f"Collection {collection} does not exist.")




