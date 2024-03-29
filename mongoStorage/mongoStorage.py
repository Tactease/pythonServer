from pymongo import MongoClient
import os
import importlib
from dotenv import load_dotenv
load_dotenv()


class MongoStorage:
    def __init__(self, entity):
        self.entityName = entity[0].lower() + entity[1:]
        model_path = os.path.join(os.path.dirname(__file__), f'../models/{self.entityName}Model')
        self.Model = importlib.import_module(model_path)
        self.collection = None
        self.connect()

    def connect(self):
        connectionURL = f'mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}'
        try:
            client = MongoClient(connectionURL)
            db = client.Tactease
            self.collection = db[self.entityName]
            print(f"Connected to {self.collection} collection")
        except Exception as e:
            print(f"connection error: {e}")


    def get_all(self):
        try:
            self.collection.find()
        except Exception as e:
            print(f"Unable to get {self.entityName}: {e}")


