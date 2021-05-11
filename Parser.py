from typing import Union, Tuple, List
from Types import *


def parse_manuscript(spell: List[Token]) -> Tuple[Optional[Union[Operator, Identifier, Literal, Bind, Return, Unsummon,
                                                                 Parameter, IO, Summon, Conjure, Enchant, Scoped,
                                                                 Conditional]], List[Token]]:
    word = spell[0]  # Get token from token list
    if word.type == Type.Identifier:
        return Identifier(word.name), spell[1:]
    if word.type == Type.Literal:
        return Literal(word.name), spell[1:]
    if word.type == Type.Separator:
        if word.name == '(':
            scoped, new_spell = parse_manuscript(spell[1:])
            if new_spell.pop(0).name != ')':
                raise Exception('Expected ")"')
            return Scoped(scoped), new_spell
        return None, spell[1:]
    if word.type == Type.Operator:
        one, new_spell = parse_manuscript(spell[1:])
        two, new_spell = parse_manuscript(new_spell)
        return Operator(word.name, one, two), new_spell
    if word.type == Type.Keyword:
        if word.name == 'bind':  # Create var
            to, new_spell = parse_manuscript(spell[1:])  # Get object to bind it too
            i, new_spell = parse_manuscript(new_spell)  # Get identifier
            val, new_spell = parse_manuscript(new_spell)  # Parse value to bind
            return Bind(i, to, val), new_spell
        if word.name == 'conjure':  # Copy object
            val, new_spell = parse_manuscript(spell[1:])
            return Conjure(val), new_spell
        if word.name == 'empty':  # New object
            return Identifier(word.name), spell[1:]
        if word.name == 'enchant':  # Copy object
            i, new_spell = parse_manuscript(spell[1:])  # Get identifier
            val, new_spell = parse_manuscript(new_spell)  # Parse function instruction line
            return Enchant(i, val), new_spell
        if word.name == 'if':
            con, new_spell = parse_manuscript(spell[1:])  # Parse condition
            bod, new_spell = parse_manuscript(new_spell)  # Parse instruction after condition
            return Conditional(con, bod), new_spell
        if word.name == 'return':  # Get value returned from function
            i, new_spell = parse_manuscript(spell[1:])
            return Return(i), new_spell
        if word.name == 'unsummon':  # Return statement
            i, new_spell = parse_manuscript(spell[1:])  # Parse return statement
            if new_spell[0].name == 'with':
                new_spell.pop(0)
                val, new_spell = parse_manuscript(new_spell)  # Parse value to return
                return Unsummon(i, val), new_spell
            return Unsummon(i, None), new_spell
        if word.name == 'set':  # assign var
            i, new_spell = parse_manuscript(spell[1:])
            val, new_spell = parse_manuscript(new_spell)
            return Set(i, Identifier('self'), val), new_spell
        if word.name == 'summon':  # Call function
            i, new_spell = parse_manuscript(spell[1:])
            parameters, new_spell = parse_parameter(new_spell)
            return Summon(i, parameters), new_spell
        if word.name == 'print':  # Print result
            v, new_spell = parse_manuscript(spell[1:])
            return IO('print', v), new_spell
        if word.name == 'read':  # Read user input
            return IO('read', None), spell[1:]
    return None, spell[1:]


def parse_parameter(spell: List[Token], first: bool = True) -> Tuple[List[Parameter], List[Token]]:
    if (first and spell[0].name == 'with') or spell[0].name == 'and':
        new_spell = spell[1:]
        i, new_spell = parse_manuscript(new_spell)
        v, new_spell = parse_manuscript(new_spell)
        next_par, new_spell = parse_parameter(new_spell, False)
        return [Parameter(i, v)] + next_par, new_spell
    return [], spell


def parse(manuscript: List[Token]) -> List[Union[Operator, Identifier, Literal, Bind, Return, Unsummon,
                                                 Parameter, IO, Summon, Conjure, Enchant, Scoped,
                                                 Conditional]]:
    out = []
    while len(manuscript) > 0:
        o, manuscript = parse_manuscript(manuscript)
        if o:  # Ignore empty lines
            out.append(o)
    return out
