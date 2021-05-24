import json, sys
from static_semantics_analyzer import main as analyze

'''
NOTE: INPUT.SECTION header will be added regardless of whether input data exists
important NOTE: make sure the identifiers are 9 characters or less, otherwise truncate

1.hlpl: 
DATA.SECTION
GLOB a +0002
GLOB b +0000
CODE.SECTION
OUT 0000 [0002] // this is lit hello's address, from literal table
HLT 0000 0000
'''
'''
2.hlpl: 
DATA.SECTION
CODE.SECTION
CALL GREET 0000
HLT 0000 0000
FUNC.GREET
OUT 0000 [0001]
HLT 0000 0000
'''
'''
3.hlpl: 
DATA.SECTION
GLOB init [0001]
CODE.SECTION
CALL GREET 0000
HLT 0000 0000 
FUNC.GREET
OUT 0000 [0002]
OUT 0000 initial
HLT 0000 0000
'''
'''
ALT 4.hlpl WITH STACK CONCEPT:
DATA.SECTION
GLOB a +0010
ENTR b +0000
CODE.SECTION
IN b 0000
CALL GREET b
// using b is not just a matter of accessing a memory cell
// because b is not global
// so here, CALL needs to push the VALUE of b onto the stack (forgetting about its address)
// and when the name b is encountered in the function
// the value is not retrieved from memory, but from the top of the stack!
// weak points: make it clear that something is a parameter to stop the function from looking in global (?)
HLT 0000 0000
FUNC.PRODUCT
MULT a b
PUSH 0000 0000  // new instruction to move from AC to top of stack
// (making the return value available)
// i.e. push onto the stack the contents of the AC
GIVE 0000 0000 // give terminates the program
// and the caller can have access to the top of the stack if the result is used
// with a POP instruction
HLT 0000 0000
'''

data_section = ['DATA.SECTION', ]
entry_code_section = ['CODE.SECTION', ]
function_code_section = []
scope = None

def create_dec(dec: list, scope: str):
    global data_section

    val = '+0000'
    sign = ''
    if len(dec) == 2:  # var
        [_, name] = dec
    elif len(dec) == 3:  # fix
        [_, name, val] = dec
    if type(val) == list:  # literal
        val = val[1]
        if type(val) == int:  # numlit
            sign = '+' if val >= 0 else '-'
            val = str(val).rjust(4, "0")
        else:  # str/charlit
            val = f'[{str(literal_table[val]).rjust(4, "0")}]'
    data_section.append(f'{scope} {name} {sign}{val}')

def create_call(call: list):
    global entry_code_section

    [name, args] = call
    # args is a list, can be empty, or have one element only (that's all we want to handle, though theoretically
    # we could do any number)
    if name == 'write':
        if len(args) > 0:
            arg = args[0]
            if type(arg) == list:  # literal
                print('ARG IS', arg)
                val = arg[1]
                line = f'OUT 0000 [{str(literal_table[val]).rjust(4, "0")}]'
            else:  # udi
                line = f'OUT 0000 {arg}'
    elif name == 'read':
        # () => read.       ========>  IN <????> 0000
        # or
        # b := () => read.  ========>  IN <address of b> 0000
        # how to remember the assignee, if it exists, in this case:
        # i think i need to implement create_assign() first, this would definitely clarify it
        line = 'IN ???? 0000'
    else:
        # function with no params: CALL <name> 0000
        # one param: CALL <name> <identifier>
        # how this works on the stack under the hood is suggested up above
        line = f'CALL {name} 0000'
    if scope == 'ENTR': entry_code_section.append(line)
    elif scope == 'FUNC': function_code_section.append(line)

def create_function_def(func: list):
    global function_code_section

    [name, _, _, body] = func  # anon: args & return_type
    # do we use args?
    function_code_section.append(f'FUNC.{name}')
    [traverse(elt) for elt in body]
    if function_code_section[-1] != 'HLT 0000 0000': function_code_section.append('HLT 0000 0000')

def create_assign(assign: list):
    [lhs, rhs] = assign
    '''
    possible cases
    b := 1. ==> MOV b +0001 OR MOV b [0001]  // assuming 1 is in address 0001
    // preference: literal option
    b := 'leila'.  ==> MOV b [0010]  // address only
    b := +(this, that).  ==> ADD this that; MOVAC b 0000   // same for all other arithmetic
    b := a. ===> MOV b a
    b := () => somefunc. ====> CALL somefunc 0000; POP 0000 0000; MOVAC b 0000
    // POP: from stack to AC
    '''
    if type(rhs) == list:
        root = rhs[0]
        # literal like ['literal', 2], operation like ['add', [a, b]], or funcall like ['funcall', ['write', a]]
        # traverse(rhs) and append corresponding code to the appropriate section: entry_code_section OR func_section
        # but to complete the corresponding code line, we need to remember b
        # => either have a global variable called assignee for assignment statements in progress
        # OR pass and return stuff across functions
        if root == 'literal':
            literal = rhs[1]
            if type(literal) == int:
                sign = '-' if literal < 0 else '+'
                line = f'MOV {lhs} {sign}{literal}'  # padding
            else:
                line = f'MOV {lhs} [{literal_table[literal]}]'  # padding
        else:
            traverse(rhs)
            # wtf
            if root == 'funcall':
                pop = 'POP 0000 0000'
                if scope == 'ENTR': entry_code_section.append(pop)
                elif scope == 'FUNC': function_code_section.append(pop)
            movac = f'MOVAC {lhs} 0000'
            if scope == 'ENTR': entry_code_section.append(movac)
            elif scope == 'FUNC': function_code_section.append(movac)
    else:
        # rhs is udi
        line = f'MOV {lhs} {rhs}'
    if scope == 'ENTR': entry_code_section.append(line)
    elif scope == 'FUNC': function_code_section.append(line)

def create_arithmetic(op: int, operands: list):
    [opd1, opd2] = operands
    line = ''
    if op == 1: line += 'ADD '
    elif op == 2: line += 'SUB '
    elif op == 3: line += 'MULT '
    elif op == 4: line += 'DIV '
    # operands can be any pair of num literals, identifiers, arithmetic operations, or function calls
    # literals and identifiers are no problem, but the others require some care
    # examples (i'm using hlpl examples, but same structure as ast):
    # +(1, 2) ==> ADD +0001 +0002
    # +(a, b) ==> ADD a b
    # +(a, 1) ==> ADD a +0001

    # +(a, +(b, c)) ==> ADD b c; MOVAC [<next available location>] 0000; ADD a [<that location>]

    # +(a, () => somefunc) ==> CALL somefunc 0000; POP 0000 0000; MOVAC [<some address>] 0000; ADD a [<that address>]

    # +((b) => somefunc, -(a, -1)) ==>
    #   CALL somefunc b; POP 0000 0000; MOVAC [<x>] 0000; SUB a -0001; MOVAC [<y>] 0000; ADD [x] [y]

    # i'll implement these last 2 cases later
    if type(opd1) == list and type(opd2) == list:
        # it could be both of them or just one of them!
        # there will be traversing, but the tricky part here is that we're building an unfinished line
        if scope == 'ENTR': entry_code_section.append('stuff')
        elif scope == 'FUNC': function_code_section.append('stuff')
    else:
        # ids
        line += f'{opd1} {opd2}'
    if scope == 'ENTR': entry_code_section.append(line)
    elif scope == 'FUNC': function_code_section.append(line)

def create_return(give: list):
    # give can be a userdefined id, an operation, a literal, or a function call
    # the way we defined PUSH, the VALUE of the returnedExpression needs to be in the AC
    # easy for number values, but what about string/char literals?
    # we'd have to use an address
    # but how can we differentiate between
    # give a.  ==> ???? PUSH 0000 0000; HLT 0000 0000
    # give 1.  ==> ADD +0001 0000; PUSH 0000 0000; HLT 0000 0000 (add to put it on the AC)
    # give +(a, b) ==> ADD a b; PUSH 0000 0000; HLT...
    # give "yes". ==> ????

    # ...
    function_code_section.append('return stuff')
    function_code_section.append('PUSH 0000 0000')
    function_code_section.append('HLT 0000 0000')

def traverse(ast: list):
    global scope

    root = ast[0]
    if root == 'program':
        scope = 'GLOB'
        [traverse(item) for item in ast[1:]]
    elif root == 'entry':
        scope = 'ENTR'
        [traverse(item) for item in ast[1:]]
    elif root == 'func':
        scope = 'FUNC'
        create_function_def(ast[1])
    elif root == 'fix' or root == 'var':
        create_dec(ast[1], scope)
    elif root == 'funcall':
        create_call(ast[1])
    elif root == 'assign':
        # ['assign', [lhs, rhs]]
        create_assign(ast[1])
    elif root == 'give':
        # when a function finishes, it pushes whatever is after 'give'
        # and halts
        create_return(ast[1])
    elif root == 'add':
        create_arithmetic(1, ast[1])
    elif root == 'sub':
        create_arithmetic(2, ast[1])
    elif root == 'mult':
        create_arithmetic(3, ast[1])
    elif root == 'div':
        create_arithmetic(4, ast[1])

    asm = ''
    for line in data_section:
        asm += line + '\n'
    for line in entry_code_section:
        asm += line + '\n'
    asm += 'HLT 0000 0000\n'
    for line in function_code_section:
        asm += line + '\n'
    asm += 'INPUT.SECTION\n'
    return asm

def main(filepath: str, default: bool, from_parser, from_analyzer, from_generator):
    global literal_table, symbol_table

    ast = analyze(filepath, default, from_parser, from_analyzer, from_generator)
    print('ast given to generator:', ast)

    with open('../milestone3/lex_output/literal_table.json') as f:
        literal_table = json.load(f)
    with open('../milestone3/lex_output/symbol_table.json') as f:
        symbol_table = json.load(f)

    asm = traverse(ast)
    print('----ASSEMBLY----')
    print(asm)
    # write to .asbl file

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        print('No HLPL input file provided for code generation, proceeding with default code from milestone3/constants.py.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default, from_parser=True, from_analyzer=True, from_generator=True)

