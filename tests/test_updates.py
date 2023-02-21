from typing import Optional
from pyddb import BaseItem
from pyddb.update import update_args, Update
from moto import mock_dynamodb2
import boto3
from pydantic import Field


def test_update_item_attribute():

    class MyItem(BaseItem):

        class Settings:
            keys = ['my_id']

        my_id: str
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

        class Settings:
            keys = ['my_id']

        my_id: str
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

        class Settings:
            keys = ['pk']

        pk: str
        something: Optional[str]

    item = FooItem(pk='foo')
    assert item.as_dict(exclude_unset=True) == {'pk': 'foo'}


def test_update_item():

    class MyItem(BaseItem):

        class Settings:
            keys = ['my_id']

        my_id: str
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


def test_null_value_attributes():

    class Foo(BaseItem):

        class Settings:
            keys = ['id']

        id: str
        something: Optional[str] = None

    item = Foo(id='foo', something=None)

    assert update_args(
        item, Update().set(), ReturnValues='ALL_OLD').get('ExpressionAttributeValues') != {':something': None}


def test_remove_attributes():

    class Foo(BaseItem):

        class Settings:
            keys = ['id']

        id: str
        age: int
        something: Optional[str]

    item = Foo(id='foo', age=25)

    args = update_args(item, Update(skip=['something']).set(), Update('something').remove())
