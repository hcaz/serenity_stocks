from pymongo import MongoClient, ReturnDocument
from dotenv import dotenv_values

config = dotenv_values(".env")
ATLAS_URI = config["ATLAS_URI"]

# MongoDB Atlas client
class AtlasClient:
    client: MongoClient

    def __init__(self, uri: str):
        self.client = MongoClient(uri)

    def get_collection(self, database_name: str, collection_name: str):
        return self.client[database_name][collection_name]
    
def getClient():
    return AtlasClient(ATLAS_URI)