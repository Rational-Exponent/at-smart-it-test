import os

from creo.data import DataModel, DatabaseFactory
from creo.data.database_interface_mongodb import MongoDBGenericDatabase

def generate_database() -> DataModel:
    """
    Generates a DataModel using MongoDB
    """

    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = os.getenv('MONGO_DB_NAME', 'creo-1')
    
    return DataModel(DatabaseFactory(MongoDBGenericDatabase, db_name=db_name, mongo_uri=mongo_uri))