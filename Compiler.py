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


def compile_line(line: Union[Summon, Conjure, Bind, Enchant, None], data, func, main, var: list):
    if line is None:
        return data, func, main, var
    if isinstance(line, Bind):
        r = compile_line(line.value, data, func, main, var)
        r[3].append(line.id.id)
        return r[0], r[1], r[2] + "\nstr r4, [r7, #" + str(get_var_num(line.id.id, r[3])) + "]", r[3]
    if isinstance(line, Conjure):
        if line.value.id == "empty":
            return data, func, main + "\
          movs r3, #129\
          lsls r3, r3, #3\
          movs r0, r3\
          bl operator new(unsigned int)\
          movs r3, r0\
          movs r4, r3\
          movs r0, r4\
          bl Spirrit::Spirrit() [complete object constructor]", var
        else:
            return data, func, main + "movs r4, [r7, #" + str(get_var_num(line.value.id, var)) + "]", var
    if isinstance(line, Enchant):
        func_name = line.id.id + str(count(func, line.id.id))
        r = compile_line(line.value, data, func, "", var)
        return data, func + [[
            line.id.id,
            r[2]
        ]], main + "ldr r3, [r7, #4]\
          ldr r3, [r3]\
          adds r1, r3, #1\
          ldr r2, [r7, #4]\
          str r1, [r2]\
        \
          ldr r2, [r7, #4]\
          lsls r3, r3, #2\
          adds r3, r2, r3\
          adds r3, r3, #4\
          ldr r2, " + func_name + "\
          str r2, [r3]", var
    if isinstance(line, Unsummon):
        r = compile_line(line.value, data, func, main, var)
        return r[0], r[1], r[2] + "pop", r[3]
    if isinstance(line, Summon):
        r = compile_line(line.parameters, data, func, main, var)
        return r[0], r[1], r[2] + "\
        push    {r4, lr}\
        movs    r0, #5\
        bl      " + line.id.id, r[3]


def compile_magic(script: List[Union[Summon, Conjure, Bind, Enchant]]) -> str:
    data, func, main, var = init_asm_file()

    for line in script:
        compile_line(line, data, func, main, var)

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
