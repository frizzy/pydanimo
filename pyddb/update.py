from typing import TYPE_CHECKING, Optional, Union, List

from attr import attr
from pyddb.attributes import item_key, asdict
from enum import Enum

if TYPE_CHECKING:
    from pyddb import BaseItem

__all__ = ['Update', 'update_args']


class AttributeReferenceError(Exception):
    pass


class Update():

    class Action(Enum):
        SET = 'SET'
        REMOVE = 'REMOVE'
        ADD = 'ADD'
        DELETE = 'DELETE'

    def __init__(self, *names):
        self.names = names
        self.action = None
        self.value = None

    def set(self, value: Optional[Union[str, int, float, list, set, dict]] = None):
        self.action = self.Action.SET
        self._validate_value(value)
        self.value = value
        return self

    def remove(self):
        self.action = self.Action.REMOVE
        return self

    def add(self):
        self.action = self.Action.ADD
        return self

    def delete(self):
        self.action = self.Action.DELETE
        return self

    def __call__(self, item: 'BaseItem', attributes: dict, expressions, names, values):

        key_attribute = item_key(item)

        for name in self.names if self.names else item.__fields__.keys():
            if name not in key_attribute:
                expressions.setdefault(self.action.value, [])
                getattr(self, f'_{self.action.value.lower()}')(name, expressions)
                names.update({f'#{name}': name})
                values.update({f':{name}': self.value if self.value else attributes[name]})

    def _set(self, name, expressions):
        expressions[self.Action.SET.value].append(f'#{name} = :{name}')

    def _validate_value(self, value):
        if value and len(self.names) != 1:
            raise AttributeReferenceError('Requires one explicit attribute name to set value')


def update_args(item: 'BaseItem', *actions, return_values: str = 'ALL_OLD'):
    attributes = asdict(item)
    expressions = {}
    names = {}
    values = {}
    for action in actions:
        action(item, attributes, expressions, names, values)

    return dict(
        Key=item_key(item),
        ReturnValues=return_values,
        UpdateExpression=' '.join([f"{key} {', '.join(value)}" for key, value in expressions.items()]),
        ExpressionAttributeValues=values,
        ExpressionAttributeNames=names
    )
