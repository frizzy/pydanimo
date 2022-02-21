import pytest
from datetime import datetime
from uuid import uuid4
from pyddb import BaseItem
from pyddb.attributes import KeyAttribute, DelimitedAttribute
from pydantic import UUID4


def test_item_key():

    class Item(BaseItem):
        id: KeyAttribute[str]

    item = Item(id='my_id')
    assert Item.key(item).as_dict() == {'id': 'my_id'}


def test_item_key_with_uuid():

    class Item(BaseItem):
        id: KeyAttribute[UUID4]

    item_id = uuid4()

    item = Item(id=item_id)
    assert Item.key(item).as_dict() == {'id': str(item_id)}


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


def test_key_item_class():

    class FooItem(BaseItem):
        foo: KeyAttribute[str]
        something: int

    key = FooItem.key(foo='barbar')

    with pytest.raises(AttributeError):
        print(key.something)

    class Foobar(BaseItem):
        foo: KeyAttribute[str]
        bar: KeyAttribute[str]

    key = Foobar.key(foo='foooo')


def test_key_compound_optionals():

    class PartitionKey(DelimitedAttribute):
        type: str = 'moo_pk'
        moo_id: UUID4

    class SortKey(DelimitedAttribute):
        type: str = 'sort_sk'
        sort_id: UUID4

    class FooItem(BaseItem):
        pk: KeyAttribute[PartitionKey]
        sk: KeyAttribute[SortKey]

    key = FooItem.key(pk=dict(moo_id=uuid4()))
