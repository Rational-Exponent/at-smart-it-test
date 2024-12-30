from typing import Optional
import time
from pymongo.collection import Collection

from creo.session import Session

class NoteType:
    id: Optional[int]
    session_id: int
    thread_id: int
    content: str
    created_at: int

    def __init__(self, session_id: int, thread_id: int, content: str, created_at: int = None, id: int = None):
        self.id = id
        self.session_id = session_id
        self.thread_id = thread_id
        self.content = content
        self.created_at = created_at if created_at is not None else int(time.time() * 1000)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'thread_id': self.thread_id,
            'content': self.content,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data: dict):
        return NoteType(
            id=data.get('_id'),
            session_id=data.get('session_id'),
            thread_id=data.get('thread_id'),
            content=data.get('content'),
            created_at=data.get('created_at')
        )

class NoteModel:
    def __init__(self, db):
        self.collection: Collection = db['notes']

    def add_note(self, note: NoteType):
        result = self.collection.insert_one(note.to_dict())
        return str(result.inserted_id)

    def get_note_by_id(self, note_id):
        data = self.collection.find_one({'_id': note_id})
        return NoteType.from_dict(data) if data else None

    def get_notes_by_thread_id(self, thread_id):
        query = {'thread_id': thread_id}
        cursor = self.collection.find(query)
        return [NoteType.from_dict(doc) for doc in cursor]
    
    def get_notes_by_session_id(self, session_id):
        query = {'session_id': session_id}
        cursor = self.collection.find(query)
        return [NoteType.from_dict(doc) for doc in cursor]

    def get_notes_by_session(self, session: Session):
        query = {'session_id': session.session_id, 'thread_id': session.thread_id}
        cursor = self.collection.find(query)
        return [NoteType.from_dict(doc) for doc in cursor]

    def update_note(self, note: NoteType):
        result = self.collection.update_one(
            {'_id': note.id},
            {'$set': note.to_dict()}
        )
        return result.modified_count > 0

    def delete_note(self, note_id):
        result = self.collection.delete_one({'_id': note_id})
        return result.deleted_count > 0
