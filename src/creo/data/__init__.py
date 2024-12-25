from .mongodb_connection import get_mongo_client

from .output import OutputModel
from .input import InputModel
from .messages import MessageModel

class DataModel():
    def __init__(self):
        # Establish a connection to MongoDB
        db = get_mongo_client()
        self.output = OutputModel(db)
        self.input = InputModel(db)
        self.messages = MessageModel(db)
