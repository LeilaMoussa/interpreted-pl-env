from parse import main as get_cst
import sys, os
import json
from cst import *

current_scope = None  # 'glob', 'entry', or 'func'; OR 1, 2, 3
in_dec = False

def is_number(operand) -> bool:
    if type(operand) == str:
        if not operand.isnumeric():
            if symbol_table[operand]['attributes']['data_type'] != 'num':
                return False
    elif type(operand) == list:
        op = operand[0]
        if op != 'add' and op != 'sub' and op != 'mult' and op != 'div':
            # must be a function call
            func_name = operand[1][0]  # bad code, i know
            if symbol_table[func_name]['attributes']['return_type'] != 'num':
                return False
    else:
        print('something fishy is going on')
        return False
    return True

def type_check_operands(opd1, opd2) -> bool:
    # operands can be any combination of numeric literals, UDIs, operations, or function calls
    # representation of numeric literal: just the number as a string, like '1'
    # UDI: just the name
    # op: since type checking will be done from the inside out, we can rest assured
    # they're represented as [<op>, [a, b]]
    # that operations are numbers
    # function calls are represented as ['funcall', [name, [args]]] 
    # ==> symbol_table[name][attributes][return_type] should be num

    return is_number(opd1) and is_number(opd2)
    # is type_check_operands() a superfluous function then?

def is_type(typespec: str, y):
    if type(y) == list:
        # op, funcall, or possibly a literal (the whole literal situation is a bit messy)
        root = y[0]
        if root == 'funcall':
            return symbol_table[y[1][0]]['attributes']["return_type"] == typespec
        elif root == 'literal':
            v = y[1]
            if type(v) == int or v.isnumeric():
                return typespec == 'num'
            elif len(v) == 3:  # because len("'L'") == 3
                return typespec == 'ascii'
            # else is string, which we haven't implemented
        elif root == 'add' or root == 'sub' or root == 'mult' or root == 'div':
            return typespec == 'num'
    elif type(y) == str:
        # UDI or numeric literal (this is NOT the best code, i know)
        if y.isnumeric():
            return typespec == 'num'
        else:
            return symbol_table[y]['attributes']['data_type'] == typespec

def has_same_type(x, y):
    # if we're in the context of an assignment, x is a variable
    # and y could be an operation ==> number, a function call, a literal, or a UDI
    # so we need to figure out what y is, get its type, and see if it's the same as x
    x_type = symbol_table[x]['attributes']['data_type']
    return is_type(x_type, y)

def match_return(returned):
    # returned is an expression or a function call, handled above
    # tricky part: efficiently retrieve name of our used defined function
    # it's much simpler for us because we're only handling one userdefined function at most
    # and of course, you could iterate over symbol_table looking for class == function,
    # but that sucks
    # since we don't have the luxury to consider efficiency, i'll just do that
    for entry in symbol_table:
        try:
            # i should get rid of this as well
            if symbol_table[entry]['attributes']['class'] == 'function':
                return is_type(symbol_table[entry]['attributes']['return_type'], returned)
        except:
            pass

def match_argument(passed: list):
    # this is tricky, because we can call 4 functions:
    # the userdefined function, entry (which should be an error), read, & write
    # so we need to give the function's name to match_argument 
    pass

def in_ref_env(identifier: str) -> bool:
    # If we're not in the middle of declaring a var/const or defining a function,
    # (in_dec is True if we're in the middle of doing that),
    # check if the identifier is within our referencing environment.
    # Two cases to raise an error:
    # 1. Undeclared identifier ==> scope = None
    # 2. Out of scope ==> scope is defined, but scope != 1 (not global)
    #       ==> scope = 2 or 3. If scope == current_scope, we're sure it's fine
    #       but even if it's not, that's not necessarily an error (think function parameters).
    #       ==> parameters: we're in scope 3 and referend exists in arguments field of that function.
    symbol_info = symbol_table[identifier]['attributes']
    symbol_scope = symbol_info['scope']
    if not symbol_scope:
        return False
    if symbol_scope == current_scope or symbol_scope == 1:
        return True
    # scope = 2 ==> in entry ==> a) ref to var/const ==> error; b) ref to function => defined because 
    # caught in one of the 2 previous conditions ==> not error
    if symbol_scope == 2:
        return symbol_info['class'] == 'function'
    # in function ===> a) ref to var/const ==> check params; b) ref to function => we don't support
    #  multiple functions anyway or recursion lol
    if symbol_scope == 3:
        if symbol_info['class'] == 'function':
            return False  # False for potentially different reasons, but error nonetheless
        for elt in symbol_info['arguments']:
            if elt['name'] == identifier:
                return True
        return False

def get_ast(cst) -> list:
    global symbol_table, current_scope, in_dec

    root = []
    _type = type(cst)
    if _type == ProgramNode:
        current_scope = 1
        root.append('program')
        # these 2 attributes of ProgramNode are always lists
        [root.append(get_ast(subtree)) for subtree in cst.declarations]
        [root.append(get_ast(subtree)) for subtree in cst.functions]
        # Program.main is of type MainNode
        root.append(get_ast(cst.main))
    elif _type == MainNode:
        current_scope = 2
        root.append('entry')
        [root.append(get_ast(subtree)) for subtree in cst.declarations]
        [root.append(get_ast(subtree)) for subtree in cst.statements]
        current_scope = 1
    elif _type == DeclarationNode:
        in_dec = True
        dec_stuff = get_ast(cst.value)
        [dt, symbol] = dec_stuff[:2]  # ['num', 'b'] for example
        _class = cst.type
        if _class == 'fix':
            [typespec, _, value] = dec_stuff
            # here, value can be a literal, a UDI, an operation, or a function call
            if not is_type(typespec, value):
                sys.exit('Oops. Type error: mismatch on constant initialization.')
            if type(value) == list:
                value = value[1]
            symbol_table[symbol]['attributes']['value'] = value
        symbol_table[symbol]['attributes']['scope'] = current_scope
        symbol_table[symbol]['attributes']['class'] = _class  # var or fix
        symbol_table[symbol]['attributes']['data_type'] = dt
        del symbol_table[symbol]['attributes']['return_type']
        del symbol_table[symbol]['attributes']['arguments']
        root.append(_class)
        root.append(dec_stuff)
        in_dec = False
    elif _type ==  VarDeclarationNode:
        typespec, ident = cst.typespec, cst.identifier
        return [get_ast(typespec), get_ast(ident)]
    elif _type == FixDeclarationNode:
        typespec, ident, value = cst.typespec, cst.identifier, cst.value
        return [get_ast(typespec), get_ast(ident), get_ast(value)]
    elif _type == TypeNode:
        return cst.value  # just a string
    elif _type == IdentifierNode:
        return get_ast(cst.value)
    elif _type == UserDefinedNode:
        ref = cst.name
        if not in_dec and not in_ref_env(ref):
            sys.exit(f'Oops. Undeclared or out-of-scope reference to {ref}')
        return ref
    elif _type == ReservedNode:
        return cst.value  # 'write' or 'read'
    elif _type == StatementNode:
        root.append(cst.type)
        root.append(get_ast(cst.value))
    elif _type == AssignmentNode:
        root.append(cst.identifier)
        # this code sucks!
        if cst.type == 'funcall':
            assign_stuff = ['funcall']
            assign_stuff.append(get_ast(cst.value))
            root.append(assign_stuff)
        else:
            root.append(get_ast(cst.value))  # exp, op, or funcall
            # i'm wondering: it doesn't even make sense to change the value! that's literally execution!
        if not has_same_type(root[0], root[1]):
            sys.exit('Oops. Type error: mismatch on assignment.')
    elif _type == ExpressionNode:
        # literal, udi, or op
        if cst.type == 'userdefined':
            return get_ast(cst.value)
        elif cst.type == 'op':
            return get_ast(cst.value)
        root.append('literal')
        root.append(get_ast(cst.value))
    elif _type == OperationNode:
        return get_ast(cst.value)    
    elif _type == OperandNode:
        return get_ast(cst.value)
    elif _type == CallNode:
        root.append(get_ast(cst.name))
        arg_stuff = []
        [arg_stuff.append(get_ast(arg)) for arg in cst.args]
        if not match_argument(arg_stuff):
            sys.exit('Oops. Type error: argument data type (or number) mismatch.')
        root.append(arg_stuff)
        ## type checking needs to be done here => need to look at symbol table for function called cst.name
        ## if the definition is not there, raise an exception
    elif _type == NumLiteralNode or _type == StringLiteralNode or _type == CharLiteralNode:
        return cst.value ## we'll see
    elif _type == ReturnNode:
        returned = get_ast(cst.value)
        if not match_return(returned):
            sys.exit('Oops. Type error: return type mismatch.')
        return returned # call or exp
    elif _type == FunctionNode:
        in_dec = True
        root.append('func')
        name = get_ast(cst.name)
        func_stuff = [name]
        symbol_table[name]['attributes']['scope'] = current_scope
        symbol_table[name]['attributes']['class'] = 'function'
        del symbol_table[name]['attributes']['address']  # address of function has no meaning at this point
        del symbol_table[name]['attributes']['data_type']
        del symbol_table[name]['attributes']['value']
        symbol_table[name]['attributes']['arguments'] = []  # we'll see if this is a convenient representation
        if len(cst.args) == 0:
            func_stuff.append([])
        else:
            for elt in cst.args:
                param = get_ast(elt)
                [data_type, param_name] = param
                symbol_table[name]['attributes']['arguments'].append({'name': param_name, 'type': data_type})
                func_stuff.append(param)
        if not cst.return_type:
            func_stuff.append(None)
        else:
            ret_type = get_ast(cst.return_type)
            symbol_table[name]['attributes']['return_type'] = ret_type
            func_stuff.append(ret_type)
        in_dec = False
        current_scope = 3
        body = []
        [body.append(get_ast(dec)) for dec in cst.declarations]
        [body.append(get_ast(stat)) for stat in cst.statements]
        func_stuff.append(body)
        root.append(func_stuff)
        current_scope = 1
    elif _type == ParamNode:
        ## params from function definition, defined with typespec and udi
        return [get_ast(cst.typespec), get_ast(cst.name)]  # these are strings
    elif _type == SelectionNode:
        root.append('if')
        root.append(get_ast(cst.condition))    # condition node
        then = []
        _else = []
        [then.append(get_ast(stat)) for stat in cst.then]    # statement nodes
        [_else.append(get_ast(stat)) for stat in cst._else]
        root.append(then)
        root.append(_else)
    elif _type == ConditionNode:
        # Again, the only type of conditions we're handling right now are pure comparisons
        # i.e. EQ & GT
        return get_ast(cst.value)
    elif _type == ComparisonNode:
        # ['eq', [a, b]]
        root.append(cst.type)  # string
        if not (is_number(get_ast(cst.comp1)) and is_number(get_ast(cst.comp2))):
            sys.exit('Oops. Type error: cannot compare non numeric values.')
        root.append([get_ast(cst.comp1), get_ast(cst.comp2)])
    elif _type == ComparedNode:
        # numlit, udi, or call
        return get_ast(cst.value)
    elif _type == LoopNode:
        # ['loop', [condition, [stats]]]
        # where 'loop' was already appended
        root.append(get_ast(cst.condition))
        body = []
        [body.append(get_ast(stat)) for stat in cst.body]
        root.append(body)
    else:
        if _type == AddNode:
            root.append('add')
        elif _type == SubNode:
            root.append('sub')
        elif _type == MultNode:
            root.append('mult')
        elif _type == DivNode:
            root.append('div')
        else:
            print('Node class does not match:', _type)
            return
        if not type_check_operands(get_ast(cst.opd1), get_ast(cst.opd2)):
            sys.exit(f'Oops. Type error: mismatched type on {root[0]} operation.')
        root.append([get_ast(cst.opd1), get_ast(cst.opd2)])
    return root
    
def main(filepath: str, default: bool, from_parser, from_analyzer, from_generator=False):
    global symbol_table

    cst = get_cst(filepath, default, from_parser, from_analyzer)
    # get symbol and literal tables from ../milestone3/lex_output/
    with open('../milestone3/lex_output/symbol_table.json') as f:
        symbol_table = json.load(f)
    if cst:
        print('Parse tree ready:')
        cst.display()
        ast = get_ast(cst)
        if from_generator:
            return ast
        else:
            print('-------AST------')
            print(ast)
        with open('../milestone3/lex_output/symbol_table.json', 'w') as op:
            op.write(json.dumps(symbol_table, indent=4))
    else:
        print("Error parsing the program -> parse tree couldn't be built.")

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        print('No HLPL input file provided for static semantics\
            analysis, proceeding with default code from milestone3/constants.py.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default, from_parser=True, from_analyzer=True)
