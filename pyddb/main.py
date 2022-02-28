from typing import Optional
from attr import attributes
from pydantic import BaseModel, create_model
from pyddb.encoders import as_dict


__all__ = ['BaseItem']


def to_str(self):
    for name in self.__fields__:
        return str(self.as_dict()[name])


class BaseItem(BaseModel):

    class Settings:
        keys = []
        indexes = {}

    @classmethod
    def key(cls, item=None, **kwargs):
        args = item.dict(exclude_unset=True) if item else kwargs
        ItemKeyClass = cls.key_class(args)
        return ItemKeyClass(**args)

    @classmethod
    def key_class(cls, args: list = []):
        return type(
            'ItemKey',
            (cls, ),
            {'__str__': to_str} if len(args) == 1 else {},
            item_keys=args
        )

    @classmethod
    def index_key(cls, name: str, item=None, **kwargs):
        args = item.dict(exclude_unset=True) if item else kwargs
        ItemKeyClass = type(
            f'ItemIndex{name.capitalize()}',
            (cls, ),
            {'__str__': to_str} if len(args) == 1 else {},
            item_keys=args.keys(),
            index=name
        )
        return ItemKeyClass(**args)

    @classmethod
    def attributes(cls, item, **kwargs):
        args = item.dict(exclude_unset=True) if item else kwargs
        ItemClass = type(
            'ItemAttributes',
            (cls, ),
            {},
            attributes=True
        )
        return ItemClass(**args)

    @classmethod
    def is_key(cls, name):
        return name in cls.Settings.keys

    @classmethod
    def match(cls, name, **kwargs):
        if issubclass(cls.__fields__[name].type_, BaseModel):
            _type = cls.__fields__[name].type_
        else:
            raise ValueError(f'{name} is not a matchable custom attribute')

        MatchClass = create_model(f'{_type.__name__}Match', __base__=_type)
        for field in MatchClass.__fields__.values():
            field.outer_type_ = Optional
            field.required = False
        return MatchClass(**kwargs)

    def as_dict(self, **kwargs):
        model = self.copy(deep=True)
        for k, v in model:
            if isinstance(v, BaseModel) and hasattr(v, 'serialize') and callable(v.serialize):
                setattr(model, k, v.serialize())

        return as_dict(model, **kwargs)

    def __init_subclass__(cls, **kwargs) -> None:

        attributes = kwargs.pop('attributes', False)
        if attributes:
            for key in list(cls.__fields__.keys()):
                if cls.is_key(key):
                    cls.__fields__.pop(key)
                    continue

            return super().__init_subclass__(**kwargs)

        item_keys = kwargs.pop('item_keys', None)
        index = kwargs.pop('index', None)

        to_optional = True
        if item_keys is not None:
            if len(item_keys) == 0:
                item_keys = cls.Settings.keys
                to_optional = False

            if index and index not in cls.Settings.indexes:
                raise ValueError(f'{index} is not a valid index')
            for key in list(cls.__fields__.keys()):
                if key not in item_keys:
                    cls.__fields__.pop(key)
                    continue
                if index and key not in cls.Settings.indexes[index]:
                    cls.__fields__.pop(key)
                    continue
                if not index and key not in cls.Settings.keys:
                    cls.__fields__.pop(key)
                    continue
                if to_optional:
                    cls.__fields__[key].outer_type_ = Optional
                    cls.__fields__[key].required = False
        super().__init_subclass__(**kwargs)
