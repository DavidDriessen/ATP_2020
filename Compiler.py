from typing import Union, List

from Types import *


def count(param, id):
    if len(param) == 0:
        return 0
    return count(param[1:], id) + (1 if param[0][0] == id else 0)


def build_function(func_id: str, lines: list, vars: list, func_var: list):
    if len(lines) > 0:
        line = lines[0]
        if isinstance(line, Enchant) and line.id.id == func_id:
            code, v = compile_line(line.value, vars, func_var)
            code2, v2 = build_function(func_id, lines[1:], v, func_var)
            return code + code2, v2
        return build_function(func_id, lines[1:], vars, func_var)
    return '', vars


def compile_functions(lines: list, func_var: list):
    if len(lines) > 0:
        line = lines[0]
        if isinstance(line, Bind):
            if isinstance(line.value, Conjure):
                code, v = compile_functions(lines[1:], func_var)
                f_code, fv = build_function(line.id.id, lines[1:], [], func_var)
                return "func_" + line.id.id + ":\npush     {lr}\nfunc_" + line.id.id + "_loop:\n" + f_code \
                       + "bl     func_" + line.id.id + "_loop\n" + code, v + [[line.id.id, fv]]
        return compile_functions(lines[1:], func_var)
    return '', []


def compile_conditional_line(line: Union[Summon, Conjure, Bind, Enchant, None], var: list, func_var: list, jup: str):
    if isinstance(line, Operator):
        codel, v = compile_line(line.left, var, func_var, 2)  # Expect literal or var
        coder, v = compile_line(line.right, v, func_var, 3)  # Expect literal or var
        code = codel + coder
        code += "cmp     r2, r3\n"
        if line.operation == '>':
            code += "ble     "
        if line.operation == '=':
            code += "bne     "
        if line.operation == '!':
            code += "beq     "
        if line.operation == '<':
            code += "bge     "
        code += jup + "\n"
        return code, v
    if isinstance(line, Scoped):
        code, v = compile_conditional_line(line.scope, var, func_var, jup)
        return code, v


def find_func_vars(func: str, func_var: list):
    for fv in func_var:
        if func == fv[0]:
            return fv
    raise Exception("No function " + func + " found")


def compile_params(func: str, params: list, var: list, func_var: list):
    if len(params) == 0:
        return 'push    {fp}\n', var
    code_value, v = compile_line(params[0].value, var, func_var, len(params) - 1)
    code_next, v = compile_params(func, params[1:], v, func_var)
    r, fv = get_var_num(params[0].id.id, find_func_vars(func, func_var)[1])
    code_id = "str     r" + str(len(params) - 1) + ", [fp, #" + str(r) + "]\n"
    return code_value + code_next + code_id, v


def compile_line(line: Union[Summon, Conjure, Bind, Enchant, None], var: list, func_var: list, register: int = None):
    if line is None:
        return "", var
    if isinstance(line, Set):
        code, v = compile_line(line.value, var, func_var, 4)
        r, v = get_var_num(line.id.id, v)
        return code + "str     r4, [fp, #" + str(r) + "]\n", v
    if isinstance(line, Unsummon):
        r = compile_line(line.value, var, func_var, 0)
        return r[0] + "bx      lr\n", r[1]
    if isinstance(line, Summon):
        code, v = compile_params(line.id.id, line.parameters, var, func_var)
        return code + "push    {lr}\n" + "bl      func_" + line.id.id + "\n", v
    if isinstance(line, Literal):
        return "mov     r" + str(register) + ", #" + line.value + "\n", var
    if isinstance(line, Identifier):
        r, v = get_var_num(line.id, var)
        return "ldr     r" + str(register) + ", [fp, #" + str(r) + "]\n", v
    if isinstance(line, Return):
        r, v = get_var_num(line.value, var)
        return "ldr     r" + str(register) + ", [fp, #" + str(r) + "]\n", v
    if isinstance(line, Operator):
        codel, v = compile_line(line.left, var, func_var, 2)  # Expect literal or var
        coder, v = compile_line(line.right, v, func_var, 3)  # Expect literal or var
        code = codel + coder
        if line.operation == '+':
            code += "add"
        if line.operation == '-':
            code += "sub"
        code += "     r" + str(register) + ", r2, r3\n"
        return code, v
    if isinstance(line, Scoped):
        code, v = compile_line(line.scope, var, func_var)
        return code, v
    if isinstance(line, Conditional):
        code, v = compile_conditional_line(line.condition, var, func_var, ".L3")
        codeb, v = compile_line(line.body, v, func_var)
        code += codeb
        code += ".L3:\n"
        return code, v
    if isinstance(line, IO):
        if line.type == 'print':
            addr, v = compile_line(line.value, var, func_var, 1)  # Expect literal or var
            code = addr
            code += "ldr     r0, .Dep\n" \
                    + "bl      std::basic_ostream<char, std::char_traits<char> >::operator<<(int)\n"
            return code, v
        if line.type == 'read':
            code = "sub     r3, fp, #28\n" \
                   + "mov     r1, r3\n" \
                   + "ldr     r0, .L7+4\n" \
                   + "bl      std::basic_istream<char, std::char_traits<char> >::operator>>(int&)\n"
            return code, var
    return '', var


def compile_lines(lines: List[Union[Summon, Conjure, Bind, Enchant]], var: list, func_var: list):
    if len(lines) == 0:
        return '', var
    code, v = compile_line(lines[0], var, func_var)
    code_next, v = compile_lines(lines[1:], v, func_var)
    return code + code_next, v


def compile_magic(script: List[Union[Summon, Conjure, Bind, Enchant]]) -> str:
    data = ".Dep:\n" \
           + ".word   _ZSt4cout\n" \
           + ".word   _ZSt3cin\n"
    func, v = compile_functions(script, [])
    main, var = compile_lines(script, [], v)
    return data + "main:\n" + main + func


def get_var_num(id: str, var: list):
    try:
        return (var.index(id) + 1) * 4, var
    except ValueError:
        return (len(var) + 1) * 4, var + [id]


def get_literal_num(var_count):
    return var_count + 4
