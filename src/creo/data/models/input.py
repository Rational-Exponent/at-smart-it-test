from typing import Optional, List
from creo.data.database_interface import GenericDatabaseInterface, DictionaryMixin
from creo.session import Session
import time


class InputType(DictionaryMixin):
    session: Session
    _id: Optional[str]
    input: str
    created_at: int

    def __init__(self, session: Session, input: str, created_at: int = None, _id: str = None):
        self.session = session
        self._id = _id
        self.input = input
        self.created_at = created_at if created_at is not None else int(time.time() * 1000)


class InputModel(GenericDatabaseInterface[InputType]):
    def __init__(self, db: GenericDatabaseInterface[InputType]):
        self.db = db

    def add_item(self, input_data: InputType) -> str:
        return self.db.add_item(input_data)

    def get_item_by_id(self, session: Session, input_id: str) -> Optional[InputType]:
        return self.db.get_item_by_id(session, input_id)

    def get_items_by_attribute(self, session: Session, attribute_name: str, attribute_value) -> List[InputType]:
        return self.db.get_items_by_attribute(session, attribute_name, attribute_value)

    def update_item(self, data: dict) -> bool:
        return self.db.update_item(data)

    def delete_item(self, session: Session, input_id: str) -> bool:
        return self.db.delete_item(session, input_id)

