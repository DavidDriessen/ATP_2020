from copy import copy
from typing import Union, Callable, List, Tuple

from Types import *


def run_operator(f: Callable[[Union[int, float, bool], Union[int, float, bool]], Union[int, float, bool]],
                 l: NamedTuple, r: NamedTuple, obj: List[NamedTuple]) -> Tuple[Union[int, float, bool], List[NamedTuple]]:
    l, obj = interpret_line(l, obj)
    r, obj = interpret_line(r, obj)
    return f(l, r), obj


def literal(value):
    if value.isnumeric():
        r = int(value)
    else:
        r = value.strip('"')
    return r


class Var(NamedTuple):
    name: str
    value: any


class Func(NamedTuple):
    code: list


class FuncReturn(NamedTuple):
    value: any


def find_var(name, stack, got=False):
    if len(stack) == 0:
        if got:
            return []
        else:
            return [None]
    if isinstance(stack[-1], Var) and stack[-1].name == name:
        if got:
            return find_var(name, stack[:-1], True)  # Garbeg collection
        return [stack[-1]] + find_var(name, stack[:-1], True) + [stack[-1].value]
    return [stack[-1]] + find_var(name, stack[:-1], got)


def interpret_code(code: List[NamedTuple], stack: List[NamedTuple]):
    new_stack = stack + interpret_line(code[0], stack)
    return interpret_code(code[1:], new_stack)


def interpret_spirit(code: List[NamedTuple], stack: List[NamedTuple] = []):
    new_stack = interpret_line(code[0], stack)
    if len(new_stack) > 0 and isinstance(new_stack[-1], FuncReturn):
        return new_stack
    return interpret_spirit(code[1:] + [code[0]], new_stack)


def interpret(code: List[NamedTuple]):
    interpret_spirit(code)


def operation(operator, l: Union[int, float, bool], r: Union[int, float, bool]) -> Union[int, float, bool]:
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
    return operators[operator](l, r)


def init_stack(parameters: List[Parameter], stack):
    if len(parameters) == 0:
        return []
    return [Var(parameters[0].id.id, interpret_line(parameters[0].value, stack)[-1])] + init_stack(parameters[1:],
                                                                                                   stack)


def interpret_line(line: NamedTuple, stack: list):
    if isinstance(line, Literal):
        return stack + [literal(line.value)]
    if isinstance(line, Identifier):
        return find_var(line.id, stack)
    if isinstance(line, Scoped):
        return stack + interpret_line(line.scope, stack)
    if isinstance(line, Bind) or isinstance(line, Set):
        r = interpret_line(line.value, stack)
        return r[:-1] + [Var(line.id.id, r[-1])]
    if isinstance(line, Conjure):
        if line.value.id == 'empty':
            return stack + [Func([])]
        else:
            return interpret_line(line.value, stack)
    if isinstance(line, Enchant):
        r = interpret_line(line.id, stack)
        f = Func(copy(r[-1].code))
        f.code.append(line.value)
        return r[:-1] + [Var(line.id.id, f)]
    if isinstance(line, IO):
        if line.type == 'print':
            s = interpret_line(line.value, stack)
            print(s[-1])
            return s[:-1]
        if line.type == 'read':
            return stack + [literal(input())]
    if isinstance(line, Return):
        r = interpret_line(line.value, stack)
        return r[:-1] + [r[-1].value]
    if isinstance(line, Operator):
        l = interpret_line(line.left, stack)
        r = interpret_line(line.right, l[:-1])
        return r[:-1] + [operation(line.operation, l[-1], r[-1])]
    if isinstance(line, Conditional):
        con = interpret_line(line.condition, stack)[-1]
        if con:
            return interpret_line(line.body, stack)
        return stack
    if isinstance(line, Summon):
        spir = interpret_line(line.id, stack)
        r = interpret_spirit(spir[-1].code, init_stack(line.parameters, stack))
        return stack + [r[-1]]
    if isinstance(line, Unsummon):
        spir = interpret_line(line.id, stack)
        if line.value:
            r = interpret_line(line.value, stack)
            return stack + [FuncReturn(r[-1])]
        return stack + [FuncReturn(None)]
