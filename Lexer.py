import re
from Types import Token, Type


def read_manuscript(script: str) -> list[Token]:
    script = re.sub(r'\(', ' ( ', script)
    script = re.sub(r'\)', ' ) ', script)
    script = re.sub(r'\n', ' \n ', script)
    return read_spell(script.split(' '))


def read_spell(spell: list[str], scope=0) -> list[Token]:
    if len(spell) == 0:
        return []
    if spell[0] == '':
        return read_spell(spell[1:], scope)
    return [gen_token(spell[0])] + read_spell(spell[1:], scope)


def is_keyword(key):
    return key in ['unsummon', 'summon', 'summonhold', 'conjure', 'enchant', 'dispel', 'bind', 'bindself', 'with',
                   'empty', 'print', 'set', 'skip', 'if', 'return', 'read', 'print']


def is_operator(key):
    return key in ['+', '-', '/', '*', '%', '=', '!=', '>', '<', '>=', '<=', 'and', 'concat']


def get_token_type(word: str) -> Type:
    if word == '(' or word == ')' or word == '\n':
        return Type.Separator
    if word.isnumeric() or (word[0] == '"' and word[-1] == '"'):
        return Type.Literal
    if is_keyword(word):
        return Type.Keyword
    if is_operator(word):
        return Type.Operator
    return Type.Identifier


def gen_token(word):
    return Token(word, get_token_type(word))


def open_manuscript(path) -> list[Token]:
    with open(path, 'r') as filename:
        manuscript = ''.join(filename.readlines())
        return read_manuscript(manuscript)
