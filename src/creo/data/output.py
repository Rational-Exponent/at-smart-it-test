from typing import Optional
import time
from pymongo.collection import Collection

from creo.session import Session

class OutputType:
    id: Optional[int]
    session_id: int
    thread_id: int
    output: str
    created_at: int

    def __init__(self, session_id: int, thread_id: int, output: str, created_at: int = None, id: int = None):
        self.id = id
        self.session_id = session_id
        self.thread_id = thread_id
        self.output = output
        self.created_at = created_at if created_at is not None else int(time.time() * 1000)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'thread_id': self.thread_id,
            'output': self.output,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data: dict):
        return OutputType(
            id=data.get('id'),
            session_id=data.get('session_id'),
            thread_id=data.get('thread_id'),
            output=data.get('output'),
            created_at=data.get('created_at')
        )

class OutputModel:
    def __init__(self, db):
        self.collection: Collection = db['outputs']

    def add_output(self, output: OutputType):
        result = self.collection.insert_one(output.to_dict())
        return str(result.inserted_id)

    def get_output_by_id(self, output_id):
        data = self.collection.find_one({'_id': output_id})
        return OutputType.from_dict(data) if data else None

    def get_outputs_by_thread_id(self, thread_id):
        query = {'thread_id': thread_id}
        cursor = self.collection.find(query)
        return [OutputType.from_dict(doc) for doc in cursor]
    
    def get_outputs_by_session_id(self, session_id):
        query = {'session_id': session_id}
        cursor = self.collection.find(query)
        return [OutputType.from_dict(doc) for doc in cursor]
    
    def get_outputs_by_session(self, session: Session):
        query = {'session_id': session.session_id, 'thread_id': session.thread_id}
        cursor = self.collection.find(query)
        return [OutputType.from_dict(doc) for doc in cursor]

    def update_output(self, output: OutputType):
        result = self.collection.update_one(
            {'_id': output.id},
            {'$set': output.to_dict()}
        )
        return result.modified_count > 0

    def delete_output(self, output_id):
        result = self.collection.delete_one({'_id': output_id})
        return result.deleted_count > 0
