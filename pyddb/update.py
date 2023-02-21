from dataclasses import MISSING
from typing import TYPE_CHECKING, Optional, Union, List
from enum import Enum
from uuid import uuid4

if TYPE_CHECKING:
    from pyddb import BaseItem

__all__ = ['Update', 'update_args']


class AttributeReferenceError(Exception):
    pass


MISSING = f'___MISSING___{str(uuid4())}'


class Update():

    class Action(Enum):
        SET = 'SET'
        REMOVE = 'REMOVE'
        ADD = 'ADD'
        DELETE = 'DELETE'

    def __init__(self, *names, skip: Optional[List[str]] = None, remove_null: bool = False):
        self.names = names
        self.action = None
        self.value = MISSING
        self.skip = skip or []
        self.remove_null = remove_null

    def set(self, value: Optional[Union[str, int, float, list, set, dict, None, bool]] = MISSING, remove_null: bool = False):
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
            if name in self.skip:
                continue
            if hasattr(item_key, name):
                continue
            if self.action == self.Action.SET:
                if self.value == MISSING and (name not in attributes or attributes[name] is None):
                    if name in attributes and attributes[name] is None and self.remove_null:
                        expressions.setdefault(self.Action.REMOVE.value, [])
                        names.update({f'#{name}': name})
                        self._remove(name, expressions)
                    continue
                if self.value is None and self.remove_null:
                    expressions.setdefault(self.Action.REMOVE.value, [])
                    names.update({f'#{name}': name})
                    self._remove(name, expressions)

            expressions.setdefault(self.action.value, [])
            getattr(self, f'_{self.action.value.lower()}')(name, expressions)
            names.update({f'#{name}': name})
            if self.action == self.Action.SET:
                values.update({f':{name}': attributes[name] if self.value == MISSING else self.value})

    def _set(self, name, expressions):
        expressions[self.Action.SET.value].append(f'#{name} = :{name}')

    def _remove(self, name, expressions):
        expressions[self.Action.REMOVE.value].append(f'#{name}')

    def _validate_value(self, value):
        if value != MISSING and len(self.names) != 1:
            raise AttributeReferenceError('Requires one explicit attribute name to set value')


def update_args(item: 'BaseItem', *actions, **kwargs):
    attributes = item.as_dict(exclude_unset=True)
    expressions = {}
    names = {}
    values = {}
    for action in actions:
        if action:
            action(item, attributes, expressions, names, values)

    return dict(
        Key=item.__class__.key(item).as_dict(),
        UpdateExpression=' '.join([f"{key} {', '.join(value)}" for key, value in expressions.items()]),
        **({'ExpressionAttributeValues': values} if values else {}),
        ExpressionAttributeNames=names,
        **kwargs
    )
