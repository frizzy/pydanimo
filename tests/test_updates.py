from pyddb import BaseItem
from pyddb.attributes import KeyAttribute
from pyddb.update import update_args, Update


def test_update_item_attribute():

    class MyItem(BaseItem):
        my_id: KeyAttribute[str]
        age: int
        eye_color: str

    item = MyItem(my_id='12345', age=473, eye_color='spotty')

    assert update_args(item, Update('age').set()) == {
        'Key': {'my_id': '12345'},
        'ReturnValues': 'ALL_OLD',
        'UpdateExpression': 'SET age = :age',
        'ExpressionAttributeValues': {':age': 473},
        'ExpressionAttributeNames': {'age': ':age'}
    }


def test_update_item_attributes():

    class MyItem(BaseItem):
        my_id: KeyAttribute[str]
        age: int
        eye_color: str

    item = MyItem(my_id='12345', age=473, eye_color='spotty')

    assert update_args(item, Update().set()) == {
        'Key': {'my_id': '12345'},
        'ReturnValues': 'ALL_OLD',
        'UpdateExpression': 'SET age = :age, eye_color = :eye_color',
        'ExpressionAttributeValues': {':age': 473, ':eye_color': 'spotty'},
        'ExpressionAttributeNames': {'age': ':age', 'eye_color': ':eye_color'}
    }
