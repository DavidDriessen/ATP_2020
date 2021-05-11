from typing import Union, List

from Compiler_helpers import *
from Types import *


def init_asm_file():
    data = ".Dep:\n" \
           ".word   _ZSt4cout\n"
    data += ".data:\n"
    main = ""
    return data, main, []


def count(param, id):
    if len(param) == 0:
        return 0
    return count(param[1:], id) + (1 if param[0][0] == id else 0)


def build_function(func_id: str, lines: list, vars: list):
    if len(lines) > 0:
        line = lines[0]
        if isinstance(line, Enchant) and line.id.id == func_id:
            code, v = compile_line(line.value, vars)
            code2, v2 = build_function(func_id, lines[1:], v)
            return code + code2, v2
        return build_function(func_id, lines[1:], vars)
    return '', vars


def compile_functions(lines: list):
    if len(lines) > 0:
        line = lines[0]
        if isinstance(line, Bind):
            if isinstance(line.value, Conjure):
                code, v = compile_functions(lines[1:])
                f_code, fv = build_function(line.id.id, lines[1:], [])
                return line.id.id + ":\n" + f_code + "\n" + code, v + fv
        return compile_functions(lines[1:])
    return '', []


def compile_line(line: Union[Summon, Conjure, Bind, Enchant, None], var: list):
    if line is None:
        return "", var
    if isinstance(line, Set):
        r = compile_line(line.value, var)
        r[1].append(line.id.id)
        return "ldr     r4, " + r[0] + "\nstr     r4, [r7, #" + str(get_var_num(line.id.id, r[1])) + "]\n", r[1]
    if isinstance(line, Unsummon):
        r = compile_line(line.value, var)
        return "ldr     r3, " + r[0] + "\nbx     lr\n", r[1]
    if isinstance(line, Summon):
        code, v = compile_line(line.parameters, var)
        return code + "\n" + \
               "push    {r4, lr}\n" + \
               "movs    r0, #5\n" + \
               "bl      .func_" + line.id.id, v
    if isinstance(line, Literal):
        return "#" + line.value, var
    if isinstance(line, Identifier):
        try:
            p = var.index(line.id)
            v = var
        except ValueError:
            p = len(var)
            v = var + [line.id]
        return "[sp, #" + str((p + 1) * 4) + "]", v
    if isinstance(line, Operator):
        codel, v = compile_line(line.left, var)  # Expect literal or var
        coder, v = compile_line(line.right, v)  # Expect literal or var
        code = "ldr     r2, " + codel + "\n"
        code += "ldr     r3, " + coder + "\n"
        code += "cmp     r2, r3\n"
        if line.operation == '>':
            code += "ble     "
        if line.operation == '=':
            code += "bne     "
        if line.operation == '!':
            code += "beq     "
        if line.operation == '<':
            code += "bge     "
        return code, v
    if isinstance(line, Scoped):
        code, v = compile_line(line.scope, var)
        return code, v
    if isinstance(line, Conditional):
        code, v = compile_line(line.condition, var)
        code += ".L3\n"
        codeb, v = compile_line(line.body, v)
        code += codeb
        code += ".L3:\n"
        return code, v
    if isinstance(line, IO):
        if line.type == 'print':
            addr, v = compile_line(line.value, var)  # Expect literal or var
            code = "ldr     r1, " + addr + "\n"
            code += "ldr     r0, .Dep\n"
            code += "bl      std::basic_ostream<char, std::char_traits<char> >::operator<<(int)\n"
            return code, v
    return '', var


def compile_lines(lines: List[Union[Summon, Conjure, Bind, Enchant]], var: list):
    if len(lines) == 0:
        return '', var
    code, v = compile_line(lines[0], var)
    code_next, v = compile_lines(lines[1:], v)
    return code + "\n" + code_next, v


def compile_magic(script: List[Union[Summon, Conjure, Bind, Enchant]]) -> str:
    data, main, var = init_asm_file()

    func, v = compile_functions(script)
    code, var = compile_lines(script, var)
    print(func)

    return data + "\n" + code + "\n" + spirit_obj + "\n" + summon_helper + "\n" + func + "\n" + main


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
