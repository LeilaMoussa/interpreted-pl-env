import json, sys
from static_semantics_analyzer import main as analyze

'''
NOTE: INPUT.SECTION header will be added regardless of whether input data exists

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
OUT 0000 [0000]
HLT 0000 0000
'''
'''
3.hlpl: 
DATA.SECTION
GLOB init [0000]  // 'L' address
// we didn't really have to rename initial to init
// because len(initial) <= 9
CODE.SECTION
CALL GREET 0000
HLT 0000 0000 
FUNC.GREET
OUT 0000 [0001]
OUT 0000 [0000]
HLT 0000 0000
'''
'''
4.hlpl: (SEE COMMENTS!)
DATA.SECTION
GLOB a +0010
ENTR b +0000
CODE.SECTION
IN b 0000
CALL GREET b
HLT 0000 0000
FUNC.PRODUCT
MULT a b
MOVAC [0002] 0000
GIVE [0002]        // using memory cells like this goes against use of a stack
// where the return value is implictly pushed by the callee & popped the caller
// i'll make changes aspa and let you know!
HLT 0000 0000

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
// and when the name b is encountered in the function definition
// the value is not retrieved from memory, but from the top of the stack!
// if you have an opinion please share :)
HLT 0000 0000
FUNC.PRODUCT
MULT a b
MOVS 0000 0000  // new instruction to move from AC to top of stack
// i.e. push onto the stack the contents of the AC
GIVE 0000 0000 // give terminates the program
// and the callee can have access to the top of the stack if the result is used
HLT 0000 0000
'''

data_section = ['DATA.SECTION', ]
code_section = ['CODE.SECTION', ]
function_section = []
scope = None

def create_dec(dec: list, scope: str):
    global data_section

    val = 0
    if len(dec) == 2:
        [_, name] = dec
    elif len(dec) == 3:
        [_, name, val] = dec
    if type(val) == list:
        val = val[1]
    data_section.append(f'{scope} {name} {val}')

def create_call(call: list):
    global code_section

    # function call: name, args (None or a single value for now)
    [name, arg] = call
    if name == 'write':
        if arg:
            # not an empty list
            [_type, val] = arg
            if _type == 'literal':
                address = literal_table[val]
                code_section.append(f'OUT 0000 [{address}]')
            else:
                code_section.append(f'OUT 0000 {val}')
    elif name == 'read':
        # () => read.       ========>  IN <????> 0000
        # or
        # b := () => read.  ========>  IN <address of b> 0000
        # how to remember the assignee, if it exists, in this case:
        # i think i need to implement create_assign() first, this would definitely clarify it
        code_section.append('IN ???? 0000')
    else:
        # function with no params: CALL <name> 0000
        # one param: CALL <name> <identifier>
        # how this works on the stack under the hood is suggested up above
        code_section.append(f'CALL {name}')

def create_function_def(func: list):
    global function_section

    # handle args if necessary here
    [name, args, return_type, body] = func
    function_section.append(f'FUNC.{name}')
    [traverse(elt) for elt in body]
    # handle return

def create_assign():
    pass

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
        create_assign()
    elif root == 'give':
        pass
    elif root == 'add':
        pass
    elif root == 'sub':
        pass
    elif root == 'mult':
        pass
    elif root == 'div':
        pass
    # maybe a couple of other language elements....

    asm = ''
    for line in data_section:
        asm += line+'\n'
    for line in code_section:
        asm += line+'\n'
    asm += 'HLT 0000 0000\n'
    ##
    asm += 'INPUT.SECTION\n'
    return asm

def main(filepath: str, default: bool, from_parser, from_analyzer, from_generator):
    global literal_table

    ast = analyze(filepath, default, from_parser, from_analyzer, from_generator)
    print('ast given to generator:', ast)

    with open('../milestone3/lex_output/literal_table.json') as f:
        literal_table = json.load(f)

    asm = traverse(ast)
    print('----ASSEMBLY----')
    print(asm)

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        print('No HLPL input file provided for code generation, proceeding with default code from milestone3/constants.py.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default, from_parser=True, from_analyzer=True, from_generator=True)

