from datetime import datetime
from uuid import uuid4
from pyddb import BaseItem
from pyddb.attributes import KeyAttribute, DelimitedAttribute, item_key, asdict
from pydantic import UUID4
from fastapi.encoders import jsonable_encoder


def test_item_key():

    class Item(BaseItem):
        id: KeyAttribute[str]

    item = Item(id='my_id')
    assert item_key(item) == {'id': 'my_id'}


def test_item_key_with_uuid():

    class Item(BaseItem):
        id: KeyAttribute[UUID4]

    item_id = uuid4()

    item = Item(id=item_id)
    assert item_key(item) == {'id': str(item_id)}


def test_item_key_with_delimited_attribute():

    class InterestingAttribute(DelimitedAttribute):

        class Settings:
            delimiter = '/'

        one: str
        two: int
        three: datetime

    class Item(BaseItem):
        id: KeyAttribute[str]
        something: KeyAttribute[InterestingAttribute]

    item = Item(id='my_id', something='ONE/2/2022-01-26T09:22:00.819Z')

    assert type(item.something.three) is datetime
