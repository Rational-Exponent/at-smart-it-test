from pymongo import MongoClient
import os

def get_mongo_client():
    # Load MongoDB configuration from environment variables or config file
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    mongo_db_name = os.getenv('MONGODB_DB_NAME', 'mydatabase')

    # Create a MongoDB client
    client = MongoClient(mongo_uri)

    # Test the connection
    try:
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("MongoDB connection successful.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

    return client[mongo_db_name]