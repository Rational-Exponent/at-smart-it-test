from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic, List, Optional
from creo.session import Session

# Define a generic type variable
T = TypeVar('T')

class GenericDatabaseInterface(ABC, Generic[T]):
    @abstractmethod
    def add_item(self, item: T) -> str:
        """Add an item to the database and return its ID."""
        # Example implementation (to be overridden)
        return "item_id"

    @abstractmethod
    def get_item_by_id(self, session: Session, item_id: int) -> Optional[T]:
        """Retrieve an item by its ID."""
        # Example implementation (to be overridden)
        return None

    @abstractmethod
    def get_items_by_attribute(self, session: Session, attribute_name: str, attribute_value) -> List[T]:
        """Retrieve items by a specific attribute."""
        # Example implementation (to be overridden)
        return []

    @abstractmethod
    def update_item(self, item: T) -> bool:
        """Update an existing item."""
        # Example implementation (to be overridden)
        return True

    @abstractmethod
    def delete_item(self, session: Session, item_id: int) -> bool:
        """Delete an item by its ID."""
        # Example implementation (to be overridden)
        return True


class DictionaryMixin:
    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        if 'session' in data and isinstance(data['session'], dict):
            data['session'] = Session.from_dict(data['session'])  # Assuming Session has a from_dict method

        instance = cls(**data)
        for key, value in data.items():
            setattr(instance, key, value)
        return instance
    
    @staticmethod
    def prop_to_dict(prop):
        # Handle primitive types directly
        if isinstance(prop, (int, str, float, bool, dict, list)):
            return prop
        # Handle objects with a `to_dict` method
        elif hasattr(prop, "to_dict"):
            return prop.to_dict()
        else:
            raise ValueError(f"Unsupported type for serialization: {type(prop)}")

    def to_dict(self) -> dict:
        # Use the instance's attributes and values for serialization
        #obj = {key: self.prop_to_dict(getattr(self, key)) for key in self.__annotations__.keys()}
        obj = {}
        for key, value in self.__dict__.items():
            if not value is None:
                if key == "_id":
                    obj[key] = str(value)
                else:
                    obj[key] = self.prop_to_dict(getattr(self, key))
        return obj