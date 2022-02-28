import pytest
from datetime import datetime
from uuid import uuid4
from pyddb import BaseItem
from pyddb.attributes import DelimitedAttribute
from pydantic import UUID4, Field


def test_item_key():

    class Item(BaseItem):

        class Settings:
            keys = ['id']

        id: str

    item = Item(id='my_id')
    assert Item.key(item).as_dict() == {'id': 'my_id'}


def test_item_key_with_uuid():

    class Item(BaseItem):

        class Settings:
            keys = ['id']

        id: UUID4

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

        class Settings:
            keys = ['id', 'something']

        id: str
        something: InterestingAttribute

    item = Item(id='my_id', something='ONE/2/2022-01-26T09:22:00.819Z')

    assert type(item.something.three) is datetime


def test_key_item_class():

    class FooItem(BaseItem):

        class Settings:
            keys = ['foo']

        foo: str
        something: int

    key = FooItem.key(foo='barbar')

    with pytest.raises(AttributeError):
        print(key.something)

    class Foobar(BaseItem):

        class Settings:
            keys = ['foo', 'bar']

        foo: str
        bar: str

    key = Foobar.key(foo='foooo')
    assert dict(key) == {'foo': 'foooo'}


def test_key_compound_optionals():

    class PartitionKey(DelimitedAttribute):
        type: str = Field('moo_pk', const=True)
        moo_id: UUID4

    class SortKey(DelimitedAttribute):
        type: str = Field('sort_sk', const=True)
        sort_id: UUID4

    class FooItem(BaseItem):

        class Settings:
            keys = ['pk', 'sk']

        pk: PartitionKey
        sk: SortKey

    foo = FooItem(pk=dict(moo_id=uuid4()), sk=SortKey(sort_id=uuid4()))

    sort_id = uuid4()
    key = FooItem.match('sk', sort_id=sort_id)

    assert str(key) == 'sort_sk#{}'.format(sort_id)
