from enum import Enum
from typing import NamedTuple, Optional


class Type(Enum):
    Separator = 1
    Literal = 2
    Keyword = 3
    Identifier = 4
    Operator = 5


class Token(NamedTuple):
    name: str
    type: Type


class Identifier(NamedTuple):
    id: str


class Summon(NamedTuple):
    id: Identifier
    parameters: list


class Literal(NamedTuple):
    value: str
    # value: Union[str, int, float]


class Bind(NamedTuple):
    id: Identifier
    to: Identifier
    value: any


class Set(NamedTuple):
    id: Identifier
    to: Identifier
    value: any


class Enchant(NamedTuple):
    id: Identifier
    value: any


class Operator(NamedTuple):
    operation: str
    left: any
    right: any


class Conditional(NamedTuple):
    condition: any
    body: any


class Conjure(NamedTuple):
    value: Identifier


class Scoped(NamedTuple):
    scope: any


class Return(NamedTuple):
    value: any


class Unsummon(NamedTuple):
    id: Identifier
    value: any


class Parameter(NamedTuple):
    id: Identifier
    value: any


class IO(NamedTuple):
    type: str
    value: Optional[any]


class Spirit(NamedTuple):
    spells: list
    bindings: dict
    running: bool
    return_v: any
