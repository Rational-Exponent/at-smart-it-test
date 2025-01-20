from typing import Optional, List
import time

from creo.session import Session
from creo.data.database_interface import GenericDatabaseInterface, DictionaryMixin


class NoteType:
    _id: Optional[int]
    session: Session
    content: str
    created_at: int

    def __init__(self, session: Session, content: str, created_at: int = None, _id: int = None):
        self.sesion = session
        self._id = _id
        self.content = content
        self.created_at = created_at if created_at is not None else int(time.time() * 1000)


class NoteModel(GenericDatabaseInterface[NoteType]):
    def __init__(self, db: GenericDatabaseInterface[NoteType]):
        self.db = db

    def add_item(self, output_data: NoteType) -> str:
        return self.db.add_item(output_data)

    def get_item_by_id(self, session: Session, output_id: str) -> Optional[NoteType]:
        return self.db.get_item_by_id(session, output_id)

    def get_items_by_attribute(self, session: Session, attribute_name: str, attribute_value) -> List[NoteType]:
        return self.db.get_items_by_attribute(session, attribute_name, attribute_value)
    
    def get_items_by_session(self, session: Session) -> List[NoteType]:
        return self.db.get_items_by_attribute(session, "session", session.to_dict())

    def update_item(self, data: dict) -> bool:
        return self.db.update_item(data)
    
    def delete_item(self, session: Session, output_id: str) -> bool:
        return self.db.delete_item(session, output_id)