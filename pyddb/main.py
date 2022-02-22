from io import UnsupportedOperation
from typing import Optional
from pydantic import BaseModel, root_validator, create_model
from pyddb.attributes import KeyAttribute, Deserializable, Serializable
from pyddb.encoders import as_dict


__all__ = ['BaseItem']


def to_str(self):
    for name in self.__fields__:
        return str(self.as_dict()[name])


class BaseItem(BaseModel):

    @classmethod
    def key(cls, item=None, **kwargs):
        args = item.dict(exclude_unset=True) if item else kwargs
        ItemKeyClass = type(
            'ItemKey',
            (cls, ),
            {'__str__': to_str} if len(args) == 1 else {},
            item_keys=args.keys()
        )
        return ItemKeyClass(**args)

    @classmethod
    def match(cls, name, **kwargs):
        if issubclass(cls.__fields__[name].type_, BaseModel):
            _type = cls.__fields__[name].type_
        elif cls.__fields__[name].sub_fields and issubclass(cls.__fields__[name].sub_fields[0].type_, BaseModel):
            _type = cls.__fields__[name].sub_fields[0].type_
        else:
            raise UnsupportedOperation(f'{name} is not a matchable custom attribute')

        MatchClass = create_model(f'{_type.__name__}Match', __base__=_type)
        for field in MatchClass.__fields__.values():
            field.outer_type_ = Optional
            field.required = False
        return MatchClass(**kwargs)

    def as_dict(self, **kwargs):
        model = self.copy(deep=True)
        for k, v in model:
            if isinstance(v, Serializable):
                setattr(model, k, v.serialize())

        return as_dict(model, **kwargs)

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
            if issubclass(field.type_, Deserializable) and key in values:
                values.update({key: field.type_.deserialize(values[key])})
            elif field.sub_fields and issubclass(field.sub_fields[0].type_, Deserializable) and key in values:
                values.update({key: field.sub_fields[0].type_.deserialize(values[key])})
        return values

    @root_validator(pre=False)
    @classmethod
    def _post_validate(cls, values):
        for key, value in values.items():
            if isinstance(value, KeyAttribute):
                values.update({key: value.value})
        return values
