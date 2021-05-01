import pymongo

class MongoDataBase():
    def __init__(self):
        self.connection_string = "mongodb://localhost:27017/"
        self.db_name = "AI_API"
        self.DB_Client = pymongo.MongoClient(self.connection_string)
        self.DB = self.DB_Client[self.db_name]
        self.delete_key = 'b339da421f0551238dcba7010211444ece30894857d608deb905babd047fb0f17a92e98287287138b4adac05e55351c3ee6aa71d1a4a99333a652f256e998dd9'

    def get_client(self):
        return self.DB_Client

    def get_DB(self):
        return self.DB

    def get_collection(self, collection):
        return self.DB[collection]

    

