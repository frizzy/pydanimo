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

    class Item(BaseModel):
        __root__: Union[ConcreteItemA, ConcreteItemB]

    item = Item.parse_obj({"pk": "hello", "sk": f"type_b#{uuid4()}"}).__root__

    assert type(item) is ConcreteItemB
