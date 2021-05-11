from typing import Union, List

from Compiler_helpers import *
from Types import *


def init_asm_file():
    data = ".data:\n"
    func = []
    main = ""
    return data, func, main, []


def count(param, id):
    if len(param) == 0:
        return 0
    return count(param[1:], id) + (1 if param[0][0] == id else 0)


def compile_functions(line: Union[Summon, Conjure, Bind, Enchant, None], funcs: dict):
    if isinstance(line, Bind):
        if isinstance(line.value, Conjure):
            funcs[line.id.id] = [line.id.id + ':\n', []]
    if isinstance(line, Enchant):
        funcs[line.id.id][0] += compile_line(line.value, funcs[line.id.id][1])


def compile_line(line: Union[Summon, Conjure, Bind, Enchant, None], var: list):
    if line is None:
        return "", var
    if isinstance(line, Bind):
        r = compile_line(line.value, var)
        r[3].append(line.id.id)
        return r[0], r[1], r[2] + "\nstr r4, [r7, #" + str(get_var_num(line.id.id, r[3])) + "]", r[3]
    if isinstance(line, Unsummon):
        r = compile_line(line.value, var)
        return r[2] + "pop", r[3]
    if isinstance(line, Summon):
        r = compile_line(line.parameters, var)
        return r[0], r[1], r[2] + "\
        push    {r4, lr}\
        movs    r0, #5\
        bl      " + line.id.id, r[3]


def compile_magic(script: List[Union[Summon, Conjure, Bind, Enchant]]) -> str:
    data, func, main, var = init_asm_file()

    for line in script:
        compile_line(line, data, var)

    return data + "\n" + spirit_obj + "\n" + summon_helper + "\n" + func + "\n" + main


def get_var_num(id, var: list):
    return (var.index(id) + 4) * 4


def get_literal_num(var_count):
    return var_count + 4


def conjure(empty, next):
    if empty:
        return "\
      movs r3, #129\
      lsls r3, r3, #3\
      movs r0, r3\
      bl operator new(unsigned int)\
      movs r3, r0\
      movs r4, r3\
      movs r0, r4\
      bl Spirrit::Spirrit() [complete object constructor]"
    else:
        return "movs r4, [r7, #" + str(get_var_num(0)) + "]"


def bind(next):
    return next + "str r4, [r7, #" + str(get_var_num(0)) + "]"


def summon(next):
    return "ldr r3, [r7, #" + str(get_var_num(0)) + "]\
          movs r0, r3\
          bl summon"
