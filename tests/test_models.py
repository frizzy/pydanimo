from typing import Union
from uuid import uuid4
from pyddb import BaseItem
from pyddb.attributes import KeyAttribute, DelimitedAttribute
from pydantic import UUID4, BaseModel, Field


def test_model_union():

    class ConcreteItemA(BaseItem):

        class SortKey(DelimitedAttribute):
            type: str = Field('type_a', const=True)
            step_id: UUID4

        pk: KeyAttribute[str]
        sk: KeyAttribute[SortKey]

    class ConcreteItemB(BaseItem):

        class SortKey(DelimitedAttribute):
            type: str = Field('type_b', const=True)
            step_id: UUID4

        pk: KeyAttribute[str]
        sk: KeyAttribute[SortKey]

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

        id: KeyAttribute[str]
        something: int
        gsi_1_pk: str
        gsi_1_sk: str

    foo = Foo(id='hello', something=2, gsi_1_pk='moo', gsi_1_sk='cow')

    assert Foo.index_key('gsi_1', gsi_1_pk='cheese') == {'gsi_1_pk': 'cheese'}
    assert str(Foo.index_key('gsi_1', gsi_1_sk='cheese')) == 'cheese'


def test_union_attribute():

    class Foo(BaseItem):

        class OddThing(DelimitedAttribute):
            type: str = 'odd_thing'
            id: UUID4

        id: KeyAttribute[str]
        something: int

        mix: Union[OddThing, str]

    foo = Foo(id='hello', something=2, mix='moo')
    assert foo.mix == 'moo'
    test_id = uuid4()
    bar = Foo(id='hello', something=2, mix=Foo.OddThing(id=test_id))
    assert bar.mix.id == test_id
