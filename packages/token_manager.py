"""TokenManager class is responsible for all operations involving authentication tokens."""
#Importing modules
import random

class TokenManager:
    
    def __init__(self):
        #There are additional eligible characters, but these should be enough
        #Allows for a total of 62^8 combinations
        self.eligible_characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.blocked_characters = """;/?:@=&$-_.+!*'(),"<>#%{ }|\^~[]`"""
        self.token_length = 8
        self.id_length = 6
        self.token_list = []
        self.id_list = []
    
    #Following methods operate on tokens

    #Randomized creation of a token, saving it in the list and returning it
    def generate_token(self):
        token = ""
        for i in range(self.token_length):
            random_number = random.randint(0, len(self.eligible_characters) - 1)
            token = "".join([token, self.eligible_characters[random_number]])
        
        #Checking conditions and regenrating, if they are not met
        if self.check_token_authenticity(token) == False:
            if self.check_token_conformity(token) == True:
                self.token_list.append(token)
            else: 
                token = self.generate_token()

        return token
            
        
    #Takes in a token as a string and checks for blocked characters, returning True for correct tokens
    def check_token_conformity(self, token: str):
        counter = 0
        if len(token) == self.token_length:
            for char in token:
                if char in self.blocked_characters:
                    counter += 1
            if counter == 0: 
                return True
            else: 
                return False
        else: 
            return False


    #Takes in a token as a string and compares to existing tokens, verifying the input, returning True for an existing token
    def check_token_authenticity(self, token: str):
        if token in  self.token_list:
            return True
        else:
            return False
        
    #Remove a token during log-out  
    def delete_token(self, token: str):
        self.token_list.remove(token)
    
    #Following methods operate on plugin IDs
    #Lots of redundant code, but this is more readable and can be individually upgraded

    #Randomized creation of an ID, saving it in the list and returning it
    def generate_id(self):
        plugin_id = ""
        for i in range(self.id_length):
            random_number = random.randint(0, len(self.eligible_characters) - 1)
            plugin_id = "".join([plugin_id, self.eligible_characters[random_number]])
        
        #Checking conditions and regenrating, if they are not met
        if self.check_id_authenticity(plugin_id) == False:
            if self.check_id_conformity(plugin_id) == True:
                self.id_list.append(plugin_id)
            else: 
                plugin_id = self.generate_token()

        return plugin_id
    
    #Takes in an id as a string and checks for blocked characters, 
    #returning True for correct tokens
    def check_id_conformity(self, plugin_id: str):
        counter = 0
        if len(plugin_id) == self.id_length:
            for char in plugin_id:
                if char in self.blocked_characters:
                    counter += 1
            if counter == 0: 
                return True
            else: 
                return False
        else: 
            return False
        
    #Takes in an id as a string and compares to existing tokens, 
    #verifying the input, 
    #returning True for an existing token
    def check_id_authenticity(self, plugin_id: str):
        if plugin_id in  self.id_list:
            return True
        else:
            return False
        
    #Remove an ID during log-out  
    def delete_id(self, plugin_id: str):
        self.id_list.remove(plugin_id)






    
        
