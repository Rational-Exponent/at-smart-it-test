from typing import Optional
import time
from pymongo.collection import Collection

from creo.session import Session

class MessageType:
    id: Optional[int]
    session_id: int  # Changed from character_id to session_id
    thread_id: int
    role: str
    content: str
    created_at: int

    def __init__(self, session_id: int, thread_id: int, role: str, content: str, created_at: int = None, id: int = None):
        self.id = id
        self.session_id = session_id  # Initialize the new field
        self.thread_id = thread_id
        self.role = role
        self.content = content
        self.created_at = created_at if created_at is not None else int(time.time() * 1000)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,  # Include in dictionary
            'thread_id': self.thread_id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data: dict):
        return MessageType(
            id=data.get('id'),
            session_id=data.get('session_id'),  # Retrieve from dictionary
            thread_id=data.get('thread_id'),
            role=data.get('role'),
            content=data.get('content'),
            created_at=data.get('created_at')
        )

class MessageModel:
    def __init__(self, db):
        self.collection: Collection = db['messages']

    def add_message(self, message: MessageType):
        result = self.collection.insert_one(message.to_dict())
        return str(result.inserted_id)

    def get_message_by_id(self, message_id):
        data = self.collection.find_one({'_id': message_id})
        return MessageType.from_dict(data) if data else None

    def get_messages_by_thread_id(self, thread_id):
        query = {'thread_id': thread_id}
        cursor = self.collection.find(query)
        return [MessageType.from_dict(doc) for doc in cursor]
    
    def get_messages_by_session_id(self, session_id):
        query = {'session_id': session_id}
        cursor = self.collection.find(query)
        return [MessageType.from_dict(doc) for doc in cursor]

    def get_messages_by_session(self, session: Session):
        query = {'session_id': session.session_id, 'thread_id': session.thread_id}
        cursor = self.collection.find(query)
        return [MessageType.from_dict(doc) for doc in cursor]

    def update_message(self, message: MessageType):
        result = self.collection.update_one(
            {'_id': message.id},
            {'$set': message.to_dict()}
        )
        return result.modified_count > 0

    def delete_message(self, message_id):
        result = self.collection.delete_one({'_id': message_id})
        return result.deleted_count > 0
