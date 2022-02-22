from typing import Optional
from pyddb import BaseItem
from pyddb.attributes import KeyAttribute
from pyddb.update import update_args, Update
from moto import mock_dynamodb2
import boto3


def test_update_item_attribute():

    class MyItem(BaseItem):
        my_id: KeyAttribute[str]
        age: int
        eye_color: str

    item = MyItem(my_id='12345', age=473, eye_color='spotty')

    assert update_args(item, Update('age').set(), ReturnValues='ALL_OLD') == {
        'Key': {'my_id': '12345'},
        'ReturnValues': 'ALL_OLD',
        'UpdateExpression': 'SET #age = :age',
        'ExpressionAttributeValues': {':age': 473},
        'ExpressionAttributeNames': {'#age': 'age'}
    }


def test_update_item_attributes():

    class MyItem(BaseItem):
        my_id: KeyAttribute[str]
        age: int
        eye_color: str

    item = MyItem(my_id='12345', age=473, eye_color='spotty')

    assert update_args(item, Update().set(), ReturnValues='ALL_OLD') == {
        'Key': {'my_id': '12345'},
        'ReturnValues': 'ALL_OLD',
        'UpdateExpression': 'SET #age = :age, #eye_color = :eye_color',
        'ExpressionAttributeValues': {':age': 473, ':eye_color': 'spotty'},
        'ExpressionAttributeNames': {'#age': 'age', '#eye_color': 'eye_color'}
    }


def test_update_item_with_optionals():

    class FooItem(BaseItem):
        pk: KeyAttribute[str]
        something: Optional[str]

    item = FooItem(pk='foo')

    # print(item.as_dict(exclude_unset=True))


def test_update_item():

    class MyItem(BaseItem):
        my_id: KeyAttribute[str]
        age: int
        eye_color: str

    item = MyItem(my_id='Foo', age=512, eye_color='pineapple')

    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')

        dynamodb.create_table(
            TableName='my_table',
            KeySchema=[{
                'AttributeName': 'my_id',
                'KeyType': 'HASH'
            }],
            AttributeDefinitions=[{
                'AttributeName': 'my_id',
                'AttributeType': 'S'
            }]
        )

        table = dynamodb.Table('my_table')

        update_response = table.update_item(**update_args(item, Update().set(), ReturnValues='ALL_NEW'))
        update_item = MyItem.parse_obj(update_response['Attributes'])

        read_response = table.get_item(Key=MyItem.key(item).as_dict())
        read_item = MyItem.parse_obj(read_response['Item'])

        assert update_item.my_id == read_item.my_id

        table.delete()
