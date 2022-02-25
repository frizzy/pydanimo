from abc import ABC
from typing import Generic, TypeVar, Union
from pydantic import BaseModel
from pydantic.fields import ModelField
from pyddb.encoders import as_dict


__all__ = ['KeyAttribute', 'DelimitedAttribute']


AttrType = TypeVar('AttrType')


class KeyAttribute(Generic[AttrType]):
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
        valid_value, error = _type.validate(v, {}, loc="value")
        if error:
            raise ValueError(str(error))
        return cls(valid_value)


class DelimitedAttribute(ABC, BaseModel):
    class Settings:
        delimiter = "#"

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, values: Union[str, dict, 'DelimitedAttribute']) -> 'DelimitedAttribute':
        if isinstance(values, cls):
            return values
        if isinstance(values, str):
            values = dict(zip(cls.__fields__.keys(), values.split(cls.Settings.delimiter)))
        return cls(**values)

    def serialize(self):
        return self.Settings.delimiter.join(map(str, as_dict(self, exclude_none=True).values()))

    def __str__(self):
        return self.serialize()
