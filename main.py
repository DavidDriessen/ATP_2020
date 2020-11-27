from Interpreter import interpret
from Lexer import open_manuscript
from Parser import parse
from Types import Spirit, Unsummon, Identifier

if __name__ == '__main__':
    code = open_manuscript("voorbeeld.txt")
    # print(code)
    code = parse(code)
    code.append(Unsummon(Identifier('self'), None))
    interpret(code)
