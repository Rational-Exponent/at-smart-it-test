from typing import Type, TypeVar, Generic
from creo.data.database_interface import GenericDatabaseInterface

T = TypeVar('T')

class DatabaseFactory(Generic[T]):
    def __init__(self, db_class: Type[GenericDatabaseInterface[T]], **kwargs):
        self.db_class = db_class
        self.kwargs = kwargs

    def create_database(self, model_type: Type[T]) -> GenericDatabaseInterface[T]:
        return self.db_class(model_type.__name__, item_class=model_type, **self.kwargs)
