from typing import TYPE_CHECKING
from pyddb.attributes import item_key, asdict
from enum import Enum

if TYPE_CHECKING:
    from pyddb import BaseItem

__all__ = ['Update', 'update_args']


class Update():

    class Action(Enum):
        SET = 'SET'
        REMOVE = 'REMOVE'
        ADD = 'ADD'
        DELETE = 'DELETE'

    def __init__(self, name: str = None):
        self.name = name
        self.action = None

    def set(self):
        self.action = self.Action.SET
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

    def __call__(self, item: 'BaseItem'):
        key_attribute = item_key(item)
        if self.action == self.Action.SET:
            if self.name:
                yield (
                    self.Action.SET.value,
                    self.name,
                    f'{self.name} = :{self.name}'
                )
            else:
                for name in item.__fields__:
                    if name not in key_attribute:
                        yield (
                            self.Action.SET.value,
                            name,
                            f'{name} = :{name}'
                        )


def update_args(item: 'BaseItem', *actions, return_values: str = 'ALL_OLD'):
    attributes = asdict(item)
    expressions = {}
    names = {}
    values = {}
    for action in actions:
        for action_type, name, expression in action(item):
            expressions.setdefault(action_type, [])
            expressions[action_type].append(expression)
            values.update({f':{name}': attributes[name]})
            names.update({name: f':{name}'})

    return dict(
        Key=item_key(item),
        ReturnValues=return_values,
        UpdateExpression=' '.join([f"{key} {', '.join(value)}" for key, value in expressions.items()]),
        ExpressionAttributeValues=values,
        ExpressionAttributeNames=names
    )
