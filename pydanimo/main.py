from typing import Generic, TypeVar, List
from pydantic import BaseModel, root_validator, ValidationError
from pydantic.fields import ModelField
from fastapi.encoders import jsonable_encoder

__all__ = [
    'BaseItem',
    'Key'
]

AttrType = TypeVar('AttrType')

class Key(Generic[AttrType]):
    def __init__(self, value):
        self.value = value

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: ModelField):
        if not field.sub_fields:
            return v
        _type = field.sub_fields[0]
        valid_value, error = _type.validate(v, {}, loc='value')
        if error:
            raise ValidationError(error, cls)
        return cls(valid_value)



class BaseItem(BaseModel):

    @root_validator(pre=False)
    @classmethod
    def _post_validate(cls, values):
        for key, value in values.items():
            if isinstance(value, Key):
                values.update({key: value.value})
        return values

    @property
    def _key(self):
        key = {}
        for name, field in self.__fields__.items():
            if issubclass(field.type_, Key):
                key.update({name: getattr(self, name)})

        return jsonable_encoder(key)

    def update(self, actions: List):
        for action in actions:
            print(action)
