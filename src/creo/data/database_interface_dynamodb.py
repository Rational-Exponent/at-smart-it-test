from typing import TypeVar, Generic, Optional, Type, List
from boto3.resources.base import ServiceResource
from boto3.dynamodb.conditions import Key
from creo.data.database_interface import GenericDatabaseInterface, DictionaryMixin

T = TypeVar('T', bound='DictionaryMixin')


class DynamoDBGenericDatabase(GenericDatabaseInterface[T]):
    def __init__(self, dynamo_table_name: str, item_class: Type[T], dynamodb_resource: ServiceResource, **kwargs):
        self.item_class = item_class
        self.table = self._table_load_or_create(dynamodb_resource, dynamo_table_name)
        

    def _table_load_or_create(self, dynamodb_resource: ServiceResource, dynamo_table_name: str):
        try:
            return dynamodb_resource.Table(dynamo_table_name)
        except dynamodb_resource.meta.client.exceptions.ResourceNotFoundException:
            key_schema = []
            attr_defs = []
            for f in self.item_class.__dict__.keys():
                if f.startswith('_'):
                    key_schema.append({'AttributeName': f[1:], 'KeyType': 'HASH'})
                    attr_defs.append({'AttributeName': f[1:], 'AttributeType': 'S'})
            return dynamodb_resource.create_table(
                TableName=dynamo_table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attr_defs,
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )

    def add_item(self, item: T) -> int:
        self.table.put_item(Item=item.to_dict())
        return item.id

    def get_item_by_id(self, item_id: int) -> Optional[T]:
        response = self.table.get_item(Key={'id': item_id})
        data = response.get('Item')
        return self.item_class.from_dict(data) if data else None

    def get_items_by_attribute(self, attribute_name: str, attribute_value: str) -> List[T]:
        response = self.table.scan(
            FilterExpression=Key(attribute_name).eq(attribute_value)
        )
        items = response.get('Items', [])
        return [self.item_class.from_dict(item) for item in items]

    def update_item(self, item: T) -> bool:
        response = self.table.update_item(
            Key={'id': item.id},
            UpdateExpression="set attribute_value=:val",
            ExpressionAttributeValues={':val': item.attribute_value},
            ReturnValues="UPDATED_NEW"
        )
        return 'Attributes' in response

    def delete_item(self, item_id: int) -> bool:
        response = self.table.delete_item(Key={'id': item_id})
        return response['ResponseMetadata']['HTTPStatusCode'] == 200
