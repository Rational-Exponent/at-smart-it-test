from typing import Optional
import time
from pymongo.collection import Collection

from creo.session import Session

class InputType:
    id: Optional[int]
    session_id: int
    thread_id: int
    input: str
    created_at: int

    def __init__(self, session_id: int, thread_id: int, input: str, created_at: int = None, id: int = None):
        self.id = id
        self.session_id = session_id
        self.thread_id = thread_id
        self.input = input
        self.created_at = created_at if created_at is not None else int(time.time() * 1000)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'thread_id': self.thread_id,
            'input': self.input,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data: dict):
        return InputType(
            id=data.get('id'),
            session_id=data.get('session_id'),
            thread_id=data.get('thread_id'),
            input=data.get('input'),
            created_at=data.get('created_at')
        )

class InputModel:
    def __init__(self, db):
        self.collection: Collection = db['inputs']

    def add_input(self, input: InputType):
        result = self.collection.insert_one(input.to_dict())
        return str(result.inserted_id)

    def get_input_by_id(self, input_id):
        data = self.collection.find_one({'_id': input_id})
        return InputType.from_dict(data) if data else None

    def get_inputs_by_thread_id(self, thread_id):
        query = {'thread_id': thread_id}
        cursor = self.collection.find(query)
        return [InputType.from_dict(doc) for doc in cursor]
    
    def get_inputs_by_session_id(self, session_id):
        query = {'session_id': session_id}
        cursor = self.collection.find(query)
        return [InputType.from_dict(doc) for doc in cursor]

    def get_inputs_by_session(self, session: Session):
        query = {'session_id': session.session_id, 'thread_id': session.thread_id}
        cursor = self.collection.find(query)
        return [InputType.from_dict(doc) for doc in cursor]

    def update_input(self, input: InputType):
        result = self.collection.update_one(
            {'_id': input.id},
            {'$set': input.to_dict()}
        )
        return result.modified_count > 0

    def delete_input(self, input_id):
        result = self.collection.delete_one({'_id': input_id})
        return result.deleted_count > 0
