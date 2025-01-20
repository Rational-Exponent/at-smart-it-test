from .models.output import OutputModel, OutputType
from .models.input import InputModel, InputType
from .models.messages import MessageModel, MessageType
from .models.notes import NoteModel, NoteType
from .database_factory import DatabaseFactory

class DataModel():
    def __init__(self, db_factory: DatabaseFactory):
        self.output = OutputModel(db=db_factory.create_database(OutputType))
        self.input = InputModel(db=db_factory.create_database(InputType))
        self.messages = MessageModel(db=db_factory.create_database(MessageType))
        self.notes = NoteModel(db=db_factory.create_database(NoteType))
