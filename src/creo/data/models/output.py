from typing import Optional, List
from creo.data.database_interface import GenericDatabaseInterface, DictionaryMixin
from creo.session import Session
import time

class OutputType(DictionaryMixin):
    session: Session
    _id: Optional[str]
    output: str
    created_at: int

    def __init__(self, session: Session, output: str, created_at: int = None, _id: str = None):
        self.session = session
        self._id = _id
        self.output = output
        self.created_at = created_at if created_at is not None else int(time.time() * 1000)


class OutputModel(GenericDatabaseInterface[OutputType]):
    def __init__(self, db: GenericDatabaseInterface[OutputType]):
        self.db = db

    def add_item(self, output_data: OutputType) -> str:
        return self.db.add_item(output_data)

    def get_item_by_id(self, session: Session, output_id: str) -> Optional[OutputType]:
        return self.db.get_item_by_id(session, output_id)

    def get_items_by_attribute(self, session: Session, attribute_name: str, attribute_value) -> List[OutputType]:
        return self.db.get_items_by_attribute(session, attribute_name, attribute_value)

    def update_item(self, data: dict) -> bool:
        return self.db.update_item(data)
    
    def delete_item(self, session: Session, output_id: str) -> bool:
        return self.db.delete_item(session, output_id)