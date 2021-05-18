from parse import main as get_cst
import sys, os
import json
from cst import *
# sys.path.append(os.path.abspath('../milestone3'))

symbol_table = {}
literal_table = {}   # do we even need this guy?
current_scope = None  # 'glob', 'entry', or 'func'; OR 1, 2, 3

def get_ast(cst) -> list:
    global symbol_table, current_scope

    root = []
    _type = type(cst)
    if _type == ProgramNode:
        current_scope = 1
        root.append('program')
        ## these 2 attributes of ProgramNode are always lists
        [root.append(get_ast(subtree)) for subtree in cst.declarations]
        [root.append(get_ast(subtree)) for subtree in cst.functions]
        # Program.main is of type MainNode
        root.append(get_ast(cst.main))
    elif _type == MainNode:
        root.append('entry')
        [root.append(get_ast(subtree)) for subtree in cst.declarations]
        [root.append(get_ast(subtree)) for subtree in cst.statements]
    elif _type == DeclarationNode:
        root.append(cst.type)
        root.append(get_ast(cst.value))
    elif _type ==  VarDeclarationNode:
        typespec, ident = cst.type, cst.identifer
        ## add type and scope to symbol table, tricky because of 'attributes' field in symbol_table
        return [get_ast(typespec), get_ast(ident)]
    elif type == FixDeclarationNode:
        typespec, ident, value = cst.type, cst.identifer, cst.value  ## value is Exp, Op, or Call
        ## again, add info AND do type checking
        return [get_ast(typespec), get_ast(ident), get_ast(value)]
    elif _type == TypeNode:
        return cst.value  # just a string
    elif _type == IdentifierNode:
        root.append(get_ast(cst.value))
    elif _type == UserDefinedNode:
        return cst.name  # just name, as string
    elif _type == ReservedNode:
        return cst.value  # 'write' or 'read'
    elif _type == StatementNode:
        root.append(cst.type)
        root.append(get_ast(cst.value))
    elif _type == AssignmentNode:
        # [<identifier_name>, <rhs, which may or may not be a list>]
        root.append(get_ast(cst.identifer))
        root.append(cst.value)
    elif _type == ExpressionNode:
        # literal or udi, we need to make a difference between these 2 types
        if cst.type != 'userdefined':
              root.append('literal')    # labeling only literal, may have to rethink this based on generator   
        root.append(get_ast(cst.value))
    elif _type == OperationNode:
        root.append(get_ast(cst.value))
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
        root.append(get_ast(cst.value))
    elif _type == CallNode:
        root.append('call')
        call_stuff = [get_ast(cst.name)]
        args = cst.args
        if len(args) == 0:
            call_stuff.append(None)
        else:
            # we'll see about this representation of parameters
            [call_stuff.append(get_cst(arg)) for arg in args]  # arg is ExpressionNode, i.e. literal or udi
            ## type checking needs to be done here => need to look at symbol table for function called cst.name
            ## if the definition is not there, raise an exception
        root.append(call_stuff)
    elif _type == NumLiteralNode or _type == StringLiteralNode or _type == CharLiteralNode:
        return cst.value ## we'll see
    elif _type == ReturnNode:
        root.append('give')
        root.append(get_ast(cst.value))  # call or exp
    elif _type == FunctionNode:
        # function definition: params, name, return DT, body (decs + statements)
        root.append('func')
        func_stuff = [cst.name]
        [func_stuff.append(param) for param in cst.args]  # i admit, idk what's the difference between arg & param
        if cst.return_type == None:
            # there's likely a better way to write this, this is ugly
            func_stuff.append(None)
        else:
            func_stuff.append(get_ast(cst.return_type))
        [func_stuff.append(dec) for dec in cst.declarations]
        [func_stuff.append(stat) for stat in cst.statements]
        root.append(func_stuff)
    elif _type == ParamNode:
        ## params from function definition, defined with typespec and udi
        return [get_ast(cst.typespec), get_ast(cst.name)]  # these are strings
    else:
        ## remaining: Selection, Loop
        print('unhandled type', _type)
    return root
    
def main(filepath: str, default: bool, from_parser, from_analyzer):
    global symbol_table, literal_table

    cst = get_cst(filepath, default, from_parser, from_analyzer)
    # get symbol and literal tables from ../milestone3/lex_output/
    with open('../milestone3/lex_output/symbol_table.json') as f:
        symbol_table = json.load(f)
    with open('../milestone3/lex_output/literal_table.json') as f:
        literal_table = json.load(f)
    if cst:
        print('Parse tree ready:')
        cst.display()
        ast = get_ast(cst)
        print(ast)
    else:
        print("Error parsing the program -> parse tree couldn't be built.")

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        print('No HLPL input file provided for static semantics \
            analysis, proceeding with default code from milestone3/constants.py.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default, from_parser=True, from_analyzer=True)
