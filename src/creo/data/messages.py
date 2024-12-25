from typing import Optional
import time

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
    
    @staticmethod
    def from_tuple(data: tuple):
        return MessageType(
            id=data[0],
            session_id=data[1],  # Handle tuple conversion
            thread_id=data[2],
            role=data[3],
            content=data[4],
            created_at=data[5]
        )

class MessageModel:
    def __init__(self, db):
        self.db = db
        self.create_table()

    def create_table(self):
        self.db.execute('''CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            session_id TEXT NOT NULL,
                            thread_id TEXT NOT NULL,
                            role TEXT NOT NULL,
                            content TEXT NOT NULL,
                            created_at INTEGER NOT NULL
                        )''')

    def add_message(self, message: MessageType):
        with self.db:
            cursor = self.db.execute('''INSERT INTO messages (session_id, thread_id, role, content, created_at)
                                        VALUES (?, ?, ?, ?, ?)''', (message.session_id, message.thread_id, message.role, message.content, message.created_at))
            self.db.commit()
            return cursor.lastrowid

    def get_message_by_id(self, message_id):
        cursor = self.db.execute('''SELECT * FROM messages WHERE id = ?''', (message_id,))
        if row := cursor.fetchone():
            return MessageType.from_tuple(row)
        else:
            return None
        
    def get_messages_by_thread_id(self, thread_id, session_id=None):
        if session_id:
            cursor = self.db.execute('''SELECT * FROM messages WHERE thread_id = ? AND session_id = ?''', (thread_id, session_id))
        else:
            cursor = self.db.execute('''SELECT * FROM messages WHERE thread_id = ?''', (thread_id,))
        return [MessageType.from_tuple(row) for row in cursor.fetchall()]
    
    def get_messages_by_session(self, session: Session):
        return self.get_messages_by_thread_id(session.thread_id, session.session_id)

    def update_message(self, message: MessageType):
        with self.db:
            cursor = self.db.execute('''UPDATE messages SET session_id = ?, thread_id = ?, role = ?, content = ?, created_at = ? WHERE id = ?''',
                            (message.session_id, message.thread_id, message.role, message.content, message.created_at, message.id))
            self.db.commit()
            return cursor.rowcount > 0

    def delete_message(self, message_id):
        with self.db:
            cursor = self.db.execute('''DELETE FROM messages WHERE id = ?''', (message_id,))
            self.db.commit()
            return cursor.rowcount > 0
