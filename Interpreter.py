from copy import deepcopy
from pprint import pprint
from typing import Union

from Types import *


def interpret(code: list, obj: Spirit):
    for line in code:
        p, obj = interpret_line(line, obj)


def run_operator(f, l, r, obj):
    l, obj = interpret_line(l, obj)
    r, obj = interpret_line(r, obj)
    return f(l, r), obj



def interpret_line(line: NamedTuple, obj: Spirit) -> tuple[Optional[Union[Spirit, str, int]], Spirit]:
    if isinstance(line, Literal):
        if line.value.isnumeric():
            r = int(line.value)
        else:
            r = line.value.strip('"')
        return r, obj
    if isinstance(line, Identifier):
        return obj.bindings[line.id], obj
    if isinstance(line, Scoped):
        return interpret_line(line.scope, obj)
    if isinstance(line, Bind):
        r, obj = interpret_line(line.value, obj)
        obj.bindings[line.id.id] = r
        return None, obj
    if isinstance(line, Conjure):
        if line.value.id == 'empty':
            return Spirit([], {}, None), obj
        else:
            return interpret_line(line.value, obj)
    if isinstance(line, Enchant):
        obj.bindings[line.id.id].spells.append(line.value)
        return None, obj
    if isinstance(line, IO):
        if line.type == 'print':
            p, obj = interpret_line(line.value, obj)
            print(p)
            return None, obj
        if line.type == 'read':
            return input(), obj
    if isinstance(line, Return):
        i, obj = interpret_line(line.value, obj)
        return i.return_v, obj
    if isinstance(line, Operator):
        operators = {
            '+': lambda l, r: l + r,
            '-': lambda l, r: l - r,
            '/': lambda l, r: l / r,
            '*': lambda l, r: l * r,
            '%': lambda l, r: l % r,
            '=': lambda l, r: l == r,
            '!=': lambda l, r: l != r,
            '>': lambda l, r: l > r,
            '<': lambda l, r: l < r,
            '>=': lambda l, r: l >= r,
            '<=': lambda l, r: l <= r,
        }
        return run_operator(operators[line.operation], line.left, line.right, obj)
    if isinstance(line, Conditional):
        con, obj = interpret_line(line.condition, obj)
        pprint(con)
        if con:
            return interpret_line(line.body, obj)
        return None, obj
    if isinstance(line, Summon):
        spir, obj = interpret_line(line.id, obj)
        spir = Spirit(deepcopy(spir.spells), {}, None)
        spir.bindings['self'] = spir
        for b in line.parameters:
            val, obj = interpret_line(b.value, obj)
            spir.bindings[b.id.id] = val
        for spell in spir.spells:
            r, spir = interpret_line(spell, spir)
        pprint(r)
        return spir, obj
    if isinstance(line, Unsummon):
        spir, obj = interpret_line(line.id, obj)
        if line.value:
            r, obj = interpret_line(line.value, obj)
            return Spirit(spir.spells, spir.bindings, r), obj
        return spir, obj
