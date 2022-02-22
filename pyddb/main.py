from datetime import datetime, date, timezone
from typing import Optional
from pydantic import BaseModel, root_validator
from pyddb.attributes import KeyAttribute, CustomAttribute
from fastapi.encoders import jsonable_encoder


__all__ = ['BaseItem']


class BaseItem(BaseModel):

    @classmethod
    def key(cls, item=None, **kwargs):
        def to_str(self):
            for name in self.__fields__:
                return self.as_dict()[name]

        args = item.dict(exclude_unset=True) if item else kwargs
        ItemKeyClass = type(
            'ItemKey',
            (cls, ),
            {'__str__': to_str} if len(args) == 1 else {},
            item_keys=args.keys()
        )
        return ItemKeyClass(**args)

    def as_dict(self, **kwargs):
        model = self.copy(deep=True)
        for k, v in model:
            if isinstance(v, CustomAttribute):
                setattr(model, k, v.serialize(BaseItem.as_dict))

        return jsonable_encoder(
            model,
            custom_encoder={
                datetime: lambda dt: (
                    f"{dt.astimezone(tz=timezone.utc).isoformat(sep='T', timespec='milliseconds')[:-6]}"
                    "Z"
                ),
                date: str
            },
            **kwargs
        )

    def __init_subclass__(cls, **kwargs) -> None:
        if (item_keys := kwargs.pop('item_keys', None)):
            for key in list(cls.__fields__.keys()):
                if not issubclass(cls.__fields__[key].type_, KeyAttribute) or key not in item_keys:
                    cls.__fields__.pop(key)
                    continue
                cls.__fields__[key].outer_type_ = Optional
                cls.__fields__[key].required = False
        super().__init_subclass__(**kwargs)

    @root_validator(pre=True)
    @classmethod
    def _pre_validate(cls, values):
        for key, field in cls.__fields__.items():
            if issubclass(field.type_, CustomAttribute) and key in values:
                values.update({key: field.type_.deserialize(values[key])})
            elif issubclass(field.type_, KeyAttribute) and issubclass(
                field.sub_fields[0].type_, CustomAttribute
            ) and key in values:
                values.update({key: field.sub_fields[0].type_.deserialize(values[key])})
        return values

    @root_validator(pre=False)
    @classmethod
    def _post_validate(cls, values):
        for key, value in values.items():
            if isinstance(value, KeyAttribute):
                values.update({key: value.value})
        return values
