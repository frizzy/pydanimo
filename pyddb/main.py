from pydantic import BaseModel, root_validator
from pyddb.attributes import KeyAttribute, CustomAttribute

__all__ = ['BaseItem']


class MissingTableResourceError(Exception):
    pass


class BaseItem(BaseModel):

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

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
