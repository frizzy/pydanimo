from typing import Optional, Union
from uuid import uuid4
from pyddb import BaseItem
from pyddb.attributes import DelimitedAttribute
from pydantic import UUID4, BaseModel, Field
from datetime import datetime


def test_model_union():

    class ConcreteItemA(BaseItem):

        class Settings:
            keys = ['pk', 'sk']

        class SortKey(DelimitedAttribute):

            type: str = Field('type_a', const=True)
            step_id: UUID4

        pk: str
        sk: SortKey

    class ConcreteItemB(BaseItem):

        class Settings:
            keys = ['pk', 'sk']

        class SortKey(DelimitedAttribute):
            type: str = Field('type_b', const=True)
            step_id: UUID4

        pk: str
        sk: SortKey

    ItemUnion = Union[ConcreteItemA, ConcreteItemB]

    class Item(BaseModel):
        item: ItemUnion

    item = Item.parse_obj({"item": {"pk": "hello", "sk": f"type_b#{uuid4()}"}})

    assert type(item.item) is ConcreteItemB


def test_indexes():

    class Foo(BaseItem):

        class Settings:
            keys = ['id']
            indexes = {
                'gsi_1': ['gsi_1_pk', 'gsi_1_sk']
            }

        id: str
        something: int
        gsi_1_pk: str
        gsi_1_sk: str

    foo = Foo(id='hello', something=2, gsi_1_pk='moo', gsi_1_sk='cow')

    assert Foo.index_key('gsi_1', gsi_1_pk='cheese') == {'gsi_1_pk': 'cheese'}
    assert str(Foo.index_key('gsi_1', gsi_1_sk='cheese')) == 'cheese'


def test_union_attribute():

    class Foo(BaseItem):

        class Settings:
            keys = ['id']

        class OddThing(DelimitedAttribute):
            type: str = Field('odd_thing', const=True)
            id: UUID4

        id: str
        something: int

        mix: Union[OddThing, str]

    foo = Foo(id='hello', something=2, mix='moo')
    assert foo.mix == 'moo'
    test_id = uuid4()
    bar = Foo(id='hello', something=2, mix=Foo.OddThing(id=test_id))
    assert bar.mix.id == test_id


def test_union_key_attribute():

    class Foo(BaseItem):

        class Settings:
            keys = ['id']

        class PartitionKey1(DelimitedAttribute):
            type: str = Field('prefix1', const=True)
            id: UUID4

        class PartitionKey2(DelimitedAttribute):
            type: str = Field('prefix2', const=True)
            id: UUID4
            other: int

        id: Union[PartitionKey1, PartitionKey2, datetime]
        something: int
        another: Optional[Union[datetime, str]]

    foo = Foo(id=dict(type='prefix1', id=uuid4()), something=1)
    assert isinstance(foo.id, Foo.PartitionKey1)

    foo = Foo(id=dict(type='prefix2', id=uuid4(), other=3), something=2)
    assert isinstance(foo.id, Foo.PartitionKey2)

    foo = Foo(id='2022-04-01T00:00:00', something=3, another='2022-04-01T00:00:00')
