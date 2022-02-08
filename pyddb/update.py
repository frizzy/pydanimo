from dataclasses import MISSING
from typing import TYPE_CHECKING, Optional, Union
from enum import Enum

from attr import attr

if TYPE_CHECKING:
    from pyddb import BaseItem

__all__ = ['Update', 'update_args']


class AttributeReferenceError(Exception):
    pass


MISSING = '___MISSING___'


class Update():

    class Action(Enum):
        SET = 'SET'
        REMOVE = 'REMOVE'
        ADD = 'ADD'
        DELETE = 'DELETE'

    def __init__(self, *names):
        self.names = names
        self.action = None
        self.value = MISSING

    def set(self, value: Optional[Union[str, int, float, list, set, dict, None, bool]] = MISSING):
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

        item_key = item.__class__.key(item)

        for name in self.names if self.names else item.__fields__.keys():
            if hasattr(item_key, name):
                continue

            if self.value == MISSING and name not in attributes:
                continue

            expressions.setdefault(self.action.value, [])
            getattr(self, f'_{self.action.value.lower()}')(name, expressions)
            names.update({f'#{name}': name})
            values.update({f':{name}': attributes[name] if self.value == MISSING else self.value})

    def _set(self, name, expressions):
        expressions[self.Action.SET.value].append(f'#{name} = :{name}')

    def _validate_value(self, value):
        if value != MISSING and len(self.names) != 1:
            raise AttributeReferenceError('Requires one explicit attribute name to set value')


def update_args(item: 'BaseItem', *actions, **kwargs):
    attributes = item.as_dict(exclude_unset=True)
    expressions = {}
    names = {}
    values = {}
    for action in actions:
        action(item, attributes, expressions, names, values)

    return dict(
        Key=item.__class__.key(item).as_dict(),
        UpdateExpression=' '.join([f"{key} {', '.join(value)}" for key, value in expressions.items()]),
        ExpressionAttributeValues=values,
        ExpressionAttributeNames=names,
        **kwargs
    )
