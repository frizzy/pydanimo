from abc import ABC, abstractmethod
from typing import Callable, Union, Generic, TypeVar, Optional, Any, TYPE_CHECKING
from pydantic import BaseModel, create_model
from pydantic.fields import ModelField


if TYPE_CHECKING:
    from pyddb import BaseItem


__all__ = ['CustomAttribute', 'KeyAttribute', 'DelimitedAttribute']


AttrType = TypeVar('AttrType')


class AttributeValidationError(Exception):
    pass


class CustomAttribute(BaseModel, ABC):
    @classmethod
    def deserialize(cls, values: Any) -> Any:
        return values

    @abstractmethod
    def serialize(self, serializer: Callable) -> Union[str, list, set, dict, None]:
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


class DelimitedAttribute(CustomAttribute):
    class Settings:
        delimiter = "#"

    _partial = None

    @classmethod
    def deserialize(cls, values):
        if isinstance(values, str):
            return dict(zip(cls.__fields__.keys(), values.split(cls.Settings.delimiter)))
        return super().deserialize(values)

    def serialize(self, serializer):
        return self.Settings.delimiter.join(map(str, serializer(self, exclude_none=True).values()))

    @classmethod
    def create_partial(cls):
        if not cls._partial:
            cls._partial = create_model(f"{cls.__name__}Partial", __base__=cls)
            for field in cls._partial.__fields__.values():
                field.outer_type_ = Optional
                field.required = False
        return cls._partial
