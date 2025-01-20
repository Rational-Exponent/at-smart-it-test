from typing import Optional, List
from creo.data.database_interface import GenericDatabaseInterface, DictionaryMixin
from creo.session import Session
import time

class MessageType(DictionaryMixin):
    session: Session
    _id: Optional[str]
    role: str
    content: str
    created_at: int

    def __init__(self, session: Session, role: str, content: str, created_at: int = None, _id: str = None):
        self._id = _id
        self.session = session
        self.role = role
        self.content = content
        self.created_at = created_at if created_at is not None else int(time.time() * 1000)
        

class MessageModel(GenericDatabaseInterface[MessageType]):
    def __init__(self, db: GenericDatabaseInterface[MessageType]):
        self.db = db

    def add_item(self, message: MessageType) -> str:
        return self.db.add_item(message)

    def get_item_by_id(self, session: Session, message_id: str) -> Optional[MessageType]:
        return self.db.get_item_by_id(session, message_id)

    def get_items_by_attribute(self, session: Session, attribute_name: str, attribute_value) -> List[MessageType]:
        return self.db.get_items_by_attribute(session, attribute_name, attribute_value)

    def get_items_by_session(self, session: Session) -> List[MessageType]:
        return self.db.get_items_by_attribute(session, "session", session.to_dict())
    
    def update_item(self, data: dict) -> bool:
        return self.db.update_item(data)

    def delete_item(self, session: Session, message_id: str) -> bool:
        return self.db.delete_item(session, message_id)
