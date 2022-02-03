from datetime import date
from pydantic import BaseModel
from pyddb import BaseItem


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
