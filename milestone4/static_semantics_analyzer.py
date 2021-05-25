from parse import main as get_cst
import sys, os
import json
from cst import *

current_scope = None  # 'glob', 'entry', or 'func'; OR 1, 2, 3

def get_ast(cst) -> list:
    global symbol_table, current_scope

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
        dec_stuff = get_ast(cst.value)
        [dt, symbol] = dec_stuff[:2]  # ['num', 'b'] for example
        _class = cst.type
        if _class == 'fix':
            value = dec_stuff[2]
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
        return cst.name  # just name, as string
    elif _type == ReservedNode:
        return cst.value  # 'write' or 'read'
    elif _type == StatementNode:
        root.append(cst.type)
        root.append(get_ast(cst.value))
    elif _type == AssignmentNode:
        root.append(get_ast(cst.identifier))
        # this code sucks!
        if cst.type == 'funcall':
            assign_stuff = ['funcall']
            assign_stuff.append(get_ast(cst.value))
            root.append(assign_stuff)
        else:
            root.append(get_ast(cst.value))  # exp, op, or funcall
            # i'm wondering: it doesn't even make sense to change the value! that's literally execution!
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
    # again, ugly repetitive code, sorry
    elif _type == AddNode:
        root.append('add')
        root.append([get_ast(cst.opd1), get_ast(cst.opd2)])
    elif _type == SubNode:
        root.append('sub')
        root.append([get_ast(cst.opd1), get_ast(cst.opd2)])
    elif _type == MultNode:
        root.append('mult')
        root.append([get_ast(cst.opd1), get_ast(cst.opd2)])
    elif _type == DivNode:
        root.append('div')
        root.append([get_ast(cst.opd1), get_ast(cst.opd2)])
    elif _type == OperandNode:
        return get_ast(cst.value)
    elif _type == CallNode:
        root.append(get_ast(cst.name))
        arg_stuff = []
        [arg_stuff.append(get_ast(arg)) for arg in cst.args]
        root.append(arg_stuff)
        ## type checking needs to be done here => need to look at symbol table for function called cst.name
        ## if the definition is not there, raise an exception
    elif _type == NumLiteralNode or _type == StringLiteralNode or _type == CharLiteralNode:
        return cst.value ## we'll see
    elif _type == ReturnNode:
        return get_ast(cst.value)  # call or exp
    elif _type == FunctionNode:
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
        print('Node class does not match:', _type)
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
