import re
from Types import Token, Type


def read_manuscript(script: str) -> list[Token]:
    # Separate separators from other words
    script = re.sub(r'\(', ' ( ', script)
    script = re.sub(r'\)', ' ) ', script)
    script = re.sub(r'\n', ' \n ', script)
    return read_spell(script.split(' '))


def read_spell(spell: list[str], scope=0) -> list[Token]:
    if len(spell) == 0:  # End of code
        return []
    if spell[0] == '':  # Ignore double spaces
        return read_spell(spell[1:], scope)
    return [gen_token(spell[0])] + read_spell(spell[1:], scope)


# Check if it is a keyword
def is_keyword(key):
    return key in ['unsummon', 'summon', 'summonhold', 'conjure', 'enchant', 'dispel', 'bind', 'bindself', 'with',
                   'empty', 'print', 'set', 'skip', 'if', 'return', 'read', 'print']


# Check if it is a operator
def is_operator(key):
    return key in ['+', '-', '/', '*', '%', '=', '!=', '>', '<', '>=', '<=', 'and', 'concat']


# Get type of word to use in token
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


# Create a token
def gen_token(word):
    return Token(word, get_token_type(word))


# Start to lex a file
def open_manuscript(path) -> list[Token]:
    with open(path, 'r') as filename:  # Open file
        manuscript = ''.join(filename.readlines())  # Read all lines from file
        return read_manuscript(manuscript)
