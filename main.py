from Interpreter import interpret
from Lexer import open_manuscript
from Parser import parse
from Types import Unsummon, Identifier

if __name__ == '__main__':
    # Open file and lex the code
    code = open_manuscript("voorbeeld.txt")
    # Parse the lexed code
    code = parse(code)
    # Add return to main loop
    code.append(Unsummon(Identifier('self'), None))
    interpret(code)
