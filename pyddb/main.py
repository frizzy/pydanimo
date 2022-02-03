from datetime import datetime, date, timezone
from pydantic import BaseModel, root_validator
from pyddb.attributes import KeyAttribute, CustomAttribute
from fastapi.encoders import jsonable_encoder


__all__ = ['BaseItem']


class BaseItem(BaseModel):

    @classmethod
    def key(cls, item=None, **kwargs):
        class ItemKey(cls, item_key=True):
            pass
        return ItemKey(**(item.dict() if item else kwargs))

    def as_dict(self, **kwargs):
        return jsonable_encoder(
            {k: v.serialize(BaseItem.as_dict) if isinstance(v, CustomAttribute) else v for k, v in self},
            custom_encoder={
                datetime: lambda dt: (
                    f"{dt.astimezone(tz=timezone.utc).isoformat(sep='T', timespec='milliseconds')[:-6]}"
                    "Z"
                ),
                date: str
            },
            **kwargs,
        )

    def __init_subclass__(cls, **kwargs) -> None:
        if kwargs.pop('item_key', False):
            for key in list(cls.__fields__.keys()):
                if not issubclass(cls.__fields__[key].type_, KeyAttribute):
                    cls.__fields__.pop(key)
        super().__init_subclass__(**kwargs)

    @root_validator(pre=True)
    @classmethod
    def _pre_validate(cls, values):
        for key, field in cls.__fields__.items():
            if issubclass(field.type_, CustomAttribute):
                values.update({key: field.type_.deserialize(values[key])})
            elif issubclass(field.type_, KeyAttribute) and issubclass(
                field.sub_fields[0].type_, CustomAttribute
            ):
                values.update({key: field.sub_fields[0].type_.deserialize(values[key])})
        return values

    @root_validator(pre=False)
    @classmethod
    def _post_validate(cls, values):
        for key, value in values.items():
            if isinstance(value, KeyAttribute):
                values.update({key: value.value})
        return values
