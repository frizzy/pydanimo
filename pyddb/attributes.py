from abc import ABC, abstractmethod
from typing import Callable, Protocol, Union, Generic, TypeVar, Any, TYPE_CHECKING
from pydantic import BaseModel
from pydantic.fields import ModelField
from pyddb.encoders import as_dict


__all__ = ['CustomAttribute', 'KeyAttribute', 'DelimitedAttribute']


AttrType = TypeVar('AttrType')


class AttributeValidationError(Exception):
    pass


class Serializable(ABC):
    @abstractmethod
    def serialize(self) -> Any:
        ...


class Deserializable(ABC):
    @classmethod
    @abstractmethod
    def deserialize(cls, values: Any) -> Any:
        ...


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
            raise AttributeValidationError(str(error))
        return cls(valid_value)


class DelimitedAttribute(Serializable, Deserializable, BaseModel):
    class Settings:
        delimiter = "#"

    @classmethod
    def deserialize(cls, values):
        if isinstance(values, str):
            return dict(zip(cls.__fields__.keys(), values.split(cls.Settings.delimiter)))
        elif isinstance(values, (cls, dict)):
            return values

    def serialize(self):
        return self.Settings.delimiter.join(map(str, as_dict(self, exclude_none=True).values()))

    def __str__(self):
        return self.serialize()
