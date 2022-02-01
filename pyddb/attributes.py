from abc import ABC, abstractmethod
from typing import Union, Generic, TypeVar, Optional, Any, TYPE_CHECKING
from datetime import datetime, date, timezone
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, create_model
from pydantic.fields import ModelField


if TYPE_CHECKING:
    from pyddb import BaseItem


__all__ = ['CustomAttribute', 'KeyAttribute', 'DelimitedAttribute', 'item_key', 'asdict']


AttrType = TypeVar('AttrType')


class AttributeValidationError(Exception):
    pass


custom_encoders = {
    datetime: lambda dt: (
        f"{dt.astimezone(tz=timezone.utc).isoformat(sep='T', timespec='milliseconds')[:-6]}"
        "Z"
    ),
    date: str
}


def asdict(item: 'BaseItem', **kwargs) -> dict:
    return jsonable_encoder(
        {k: v.serialize() if isinstance(v, CustomAttribute) else v for k, v in item},
        custom_encoder=custom_encoders,
        **kwargs,
    )


class CustomAttribute(BaseModel, ABC):
    @classmethod
    def deserialize(cls, values: Any) -> Any:
        return values

    @abstractmethod
    def serialize(self) -> Union[str, list, set, dict, None]:
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

    def serialize(self):
        return self.Settings.delimiter.join(map(str, asdict(self, exclude_none=True).values()))

    @classmethod
    def create_partial(cls):
        if not cls._partial:
            cls._partial = create_model(f"{cls.__name__}Partial", __base__=cls)
            for field in cls._partial.__fields__.values():
                field.outer_type_ = Optional
                field.required = False
        return cls._partial


def item_key(item: 'BaseItem'):
    return asdict(item, exclude=set([
        name for name, field in item.__fields__.items() if not issubclass(field.type_, KeyAttribute)
    ]))
