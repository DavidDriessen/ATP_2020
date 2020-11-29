from typing import Union
from Types import *


def parse_manuscript(spell: list[Token]) -> tuple[Optional[Union[Operator, Identifier, Literal, Bind, Return, Unsummon,
                                                                 Parameter, IO, Summon, Conjure, Enchant, Scoped,
                                                                 Conditional]], list[Token]]:
    word = spell.pop(0)
    if word.type == Type.Identifier:
        return Identifier(word.name), spell
    if word.type == Type.Literal:
        return Literal(word.name), spell
    if word.type == Type.Separator:
        if word.name == '(':
            scoped, spell = parse_manuscript(spell)
            if spell.pop(0).name != ')':
                raise Exception('Expected ")"')
            return Scoped(scoped), spell
        return None, spell
        # return parse_manuscript(spell)
    if word.type == Type.Operator:
        one, spell = parse_manuscript(spell)
        two, spell = parse_manuscript(spell)
        return Operator(word.name, one, two), spell
    if word.type == Type.Keyword:
        if word.name == 'bind':  # Create var
            to, spell = parse_manuscript(spell)
            i, spell = parse_manuscript(spell)
            val, spell = parse_manuscript(spell)
            return Bind(i, to, val), spell
        if word.name == 'conjure':  # Call function
            val, spell = parse_manuscript(spell)
            return Conjure(val), spell
        if word.name == 'empty':  # New object
            return Identifier(word.name), spell
        if word.name == 'enchant':
            i, spell = parse_manuscript(spell)
            val, spell = parse_manuscript(spell)
            return Enchant(i, val), spell
        if word.name == 'if':
            con, spell = parse_manuscript(spell)
            bod, spell = parse_manuscript(spell)
            return Conditional(con, bod), spell
        if word.name == 'return':
            i, spell = parse_manuscript(spell)
            return Return(i), spell
        if word.name == 'unsummon':  # return statement
            i, spell = parse_manuscript(spell)
            if spell[0].name == 'with':
                spell.pop(0)
                val, spell = parse_manuscript(spell)
                return Unsummon(i, val), spell
            return Unsummon(i, None), spell
        if word.name == 'set':  # assign var
            i, spell = parse_manuscript(spell)
            val, spell = parse_manuscript(spell)
            return Bind(i, Identifier('self'), val), spell
        if word.name == 'summon':  # Call function
            i, spell = parse_manuscript(spell)
            parameters, spell = parse_parameter(spell)
            return Summon(i, parameters), spell
        if word.name == 'print':  # Print result
            v, spell = parse_manuscript(spell)
            return IO('print', v), spell
        if word.name == 'read':  # Read user input
            return IO('read', None), spell
    return None, spell


def parse_parameter(spell, first=True):
    if (first and spell[0].name == 'with') or spell[0].name == 'and':
        spell.pop(0)
        i, spell = parse_manuscript(spell)
        v, spell = parse_manuscript(spell)
        next, spell = parse_parameter(spell, False)
        return [Parameter(i, v)] + next, spell
    return [], spell


def parse(manuscript):
    out = []
    while len(manuscript) > 0:
        o, manuscript = parse_manuscript(manuscript)
        if o:  # Ignore empty lines
            out.append(o)
    return out
