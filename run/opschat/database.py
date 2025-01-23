import os
from creo.data import DataModel, DatabaseFactory
from creo.data.database_interface_mongodb import MongoDBGenericDatabase

def generate_datase():
    """
    Generates a DataModel using MongoDB
    """

    mongo_uri = os.getenv('MONGO_URI') or "localhost"
    db_name = os.getenv('MONGO_DB_NAME') or "opschat-db"
    
    return DataModel(DatabaseFactory(MongoDBGenericDatabase, db_name=db_name, mongo_uri=mongo_uri))