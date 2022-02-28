from abc import ABC
from typing import TypeVar, Union
from pydantic import BaseModel
from pyddb.encoders import as_dict


__all__ = ['DelimitedAttribute']


AttrType = TypeVar('AttrType')


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
