import json, sys
from static_semantics_analyzer import main as analyze

'''
NOTE: make sure the identifiers are 9 characters or less, otherwise truncate
SPICY ADDITION: capitalize identifiers + if we have time, beautify assembly with space padding

1.hlpl: 
DATA.SECTION
GLOB a +0002
GLOB b +0000
CODE.SECTION
OUT 0000 [0002] // this is lit hello's address, from literal table
HLT 0000 0000
INPUT.SECTION
-----------------------------------
2.hlpl: 
DATA.SECTION
CODE.SECTION
CALL GREET 0000
HLT 0000 0000
FUNC.GREET
OUT 0000 [0001]
HLT 0000 0000
INPUT.SECTION
-------------------------
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
INPUT.SECTION
-----------------------------------------
4.hlpl:
DATA.SECTION
GLOB a +0010
ENTR b +0000
CODE.SECTION
IN b 0000
CALL product b
HLT 0000 0000
FUNC.PRODUCT
MULT a b
PUSH 0000 0000
HLT 0000 0000
// using b is not just a matter of accessing a memory cell
// because b is not global
// so here, CALL needs to push the VALUE of b onto the stack (forgetting about its address)
// and when the name b is encountered in the function
// the value is not retrieved from memory, but from the top of the stack!
// weak points: make it clear that something is a parameter to stop the function from looking in global (?)
// new instruction to move from AC to top of stack
// (making the return value available)
// i.e. push onto the stack the contents of the AC
// give terminates the program
// and the caller can have access to the top of the stack if the result is used
// with a POP instruction
'''

data_section = ['DATA.SECTION', ]
entry_code_section = ['CODE.SECTION', ]
function_code_section = []
scope = None

def create_dec(dec: list, scope: str):
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
    [name, args] = call
    # args is a list, can be empty, or have one element only (that's all we want to handle, though theoretically
    # we could do any number)
    if name == 'write':
        if len(args) > 0:
            arg = args[0]
            if type(arg) == list:  # literal
                val = arg[1]
                line = f'OUT 0000 [{str(literal_table[val]).rjust(4, "0")}]'
            else:  # udi
                line = f'OUT 0000 {arg}'
    elif name == 'read':
        # read is usually used as the RHS of an assignment
        # in which case, create_assign() would take care of that
        # so this code is very unlikely to execute
        # because it corresponds to the standalone statement () => read.
        # if it's not explicitly assigned anywhere, it should be disposed of simply
        # but the question is where it should be put?
        line = 'IN ???? 0000'
    else:
        # function with no params: CALL <name> 0000
        # one param: CALL <name> <identifier>
        # how this works on the stack under the hood is suggested up above
        line = f'CALL {name} '
        if len(args) == 0:
            line += '0000'
        else:
            # arguments are expressions
            arg = args[0]
            # again, we're only implementing one argument on purpose, 
            # though theoretically it would be pretty easy to accommodate any number
            if type(arg) == list:
                # literal or operation
                # requires preceding assembly instructions and saving in memory (or stack right away, idk)
                pass
            else:
                # udi
                # pickle: PUSHING HERE? DOABLE? REASONABLE? CONSISENT?
                line += arg  # identifier name
    if scope == 'ENTR': entry_code_section.append(line)
    elif scope == 'FUNC': function_code_section.append(line)

def create_function_def(func: list):
    [name, _, _, body] = func  # anon: args & return_type
    function_code_section.append(f'FUNC.{name}')
    [traverse(elt) for elt in body]
    if function_code_section[-1] != 'HLT 0000 0000': function_code_section.append('HLT 0000 0000')

def create_assign(assign: list):
    [lhs, rhs] = assign
    line = ''  # just a hack, looks bad
    '''
    possible cases
    b := 1. ==> MOV b +0001 OR MOV b [0001]  // assuming 1 is in address 0001
    // preference: literal option
    b := 'leila'.  ==> MOV b [0010]  // address only
    b := +(this, that).  ==> ADD this that; MOVAC b 0000   // same for all other arithmetic
    b := a. ===> MOV b a
    b := () => somefunc. ====> CALL somefunc 0000; POP 0000 0000; MOVAC b 0000
    b := () => read. ====> IN b 0000  // this is the most exceptional one
    // POP: from stack to AC
    '''
    if type(rhs) == list:
        [root, body] = rhs
        if root == 'literal':
            literal = rhs[1]
            if type(literal) == int:
                sign = '-' if literal < 0 else '+'
                line = f'MOV {lhs} {sign}{literal}'  # padding
            else:
                line = f'MOV {lhs} [{literal_table[literal]}]'  # padding
        elif root == 'funcall':
            # read, write, or userdefined function
            # 1. read:  IN <lhs> 0000
            # 2. write: shouldn't happen because it makes no sense, so won't bother writing the expected result
            # 3. userdefined: CALL, POP, MOVAC (remember, MOVAC means move OUT of the AC)
            if body[0] == 'read':
                # why bother call traverse here if the result is so easy to get like this? => not very elegant, but i can live with that
                line = f'IN {lhs} 0000'
            else:  # assuming the hlpl writer isn't crazy enough to use write, though that wouldn't be an issue for code generation
                traverse(rhs)
                pop = 'POP 0000 0000'  # to use the return value, put in AC
                movac = f'MOVAC {lhs} 0000'  # put return value in LHS
                if scope == 'ENTR':
                    entry_code_section.append(pop)
                    entry_code_section.append(movac)
                elif scope == 'FUNC':
                    function_code_section.append(pop)
                    function_code_section.append(movac)
        else:
            # arithmetic operation
            # also involves MOVAC, not MOV, so the last few lines of this function are pretty dumb
            pass
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
        line += 'stuff'
    else:
        # just userdefined ids
        line += f'{opd1} {opd2}'
    if scope == 'ENTR': entry_code_section.append(line)
    elif scope == 'FUNC': function_code_section.append(line)

def create_return(given: list):
    # given can be a userdefined id, an operation, a literal, or a function call
    # the way we defined PUSH, the VALUE of the returnedExpression needs to be in the AC
    # easy for number values, but what about string/char literals?
    # we'd have to use an address
    # but how can we differentiate between
    # give a.  ==> ???? PUSH 0000 0000; HLT 0000 0000
    # give 1.  ==> ADD +0001 0000; PUSH 0000 0000; HLT 0000 0000 (add to put it on the AC)
    # give +(a, b) ==> ADD a b; PUSH 0000 0000; HLT...
    # give "yes". ==> ????
    traverse(given)
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

