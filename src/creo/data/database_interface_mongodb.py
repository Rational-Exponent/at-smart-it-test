from typing import TypeVar, Generic, List, Optional, Dict, Any, Type
from pymongo import MongoClient
from pymongo.collection import Collection
from bson import ObjectId
from creo.data.database_interface import GenericDatabaseInterface, DictionaryMixin
from creo.session import Session

T = TypeVar('T', bound='DictionaryMixin')


class MongoDBGenericDatabase(GenericDatabaseInterface[T]):
    def __init__(self, collection_name: str, item_class: Type[T], db_name: str, mongo_uri: str = "mongodb://localhost:27017", **kwargs):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection: Collection = self.db[collection_name]
        self.item_class = item_class

    def add_item(self, item: T) -> str:
        result = self.collection.insert_one(item.to_dict())
        return str(result.inserted_id)

    def get_item_by_id(self, session: Session, item_id: str) -> Optional[T]:
        data = self.collection.find_one({
                "_id": ObjectId(item_id),
                "session": session.to_dict()
            })
        return self.item_class.from_dict(data) if data else None

    def get_items_by_attribute(self, session: Session, attribute_name: str, attribute_value: Any) -> List[T]:
        cursor = self.collection.find(
            {
                "session": session.to_dict(),
                attribute_name: attribute_value
            })
        return [self.item_class.from_dict(doc) for doc in cursor]

    def update_item(self, item: T) -> bool:
        update_obj = item.to_dict()
        item_id = update_obj.pop("_id")
        result = self.collection.replace_one(
            {
                "session": item.session.to_dict(),
                "_id": ObjectId(item_id)
            }, 
            update_obj)
        return result.modified_count > 0

    def delete_item(self, session: Session, item_id: str) -> bool:
        result = self.collection.delete_one({
                "session": session.to_dict(),
                "_id": ObjectId(item_id)
            })
        return result.deleted_count > 0
