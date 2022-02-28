from typing import Optional
from datetime import date
from pydantic import BaseModel, Field
from pyddb import BaseItem
from pyddb.attributes import DelimitedAttribute


def test_asdict():

    class PersonAttribute(BaseModel):
        firstname: str
        lastname: str
        date_of_birth: date

    class Item(BaseItem):

        id: str
        person: PersonAttribute

    item = Item(id='my_id', person={'firstname': 'Max', 'lastname': 'van Steen', 'date_of_birth': '1996-08-03'})

    assert type(item.person.date_of_birth) is date

    assert item.as_dict() == {
        'id': 'my_id', 'person': {'firstname': 'Max', 'lastname': 'van Steen', 'date_of_birth': '1996-08-03'}
    }


def test_get_non_key_attributes():

    class FooItem(BaseItem):

        class Settings:
            keys = ['id']

        id: str
        something: int
        more: str

    foo = FooItem(id='my_id', something=1, more='something')
    assert FooItem.attributes(foo) == {'something': 1, 'more': 'something'}


def test_optional_matchable_attribute():

    class FooItem(BaseItem):

        class MatchAttr(DelimitedAttribute):
            type: str = Field('prefix', const=True)
            match: str

        class Settings:
            keys = ['id']

        id: str
        something: Optional[MatchAttr]

    item = FooItem(id='my_id', something={'match': 'something'})
    print(FooItem.match('something'))

    assert item.as_dict() == {'id': 'my_id', 'something': 'prefix#something'}
