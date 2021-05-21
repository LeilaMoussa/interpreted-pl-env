import json

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
    data_section.append(f'{scope} {name} {val}')  ## formatting and stuff, whatever

def create_call(call: list):
    global code_section

    # if we ever back out of the one-function decision, we need to specify code_section
    # or func_section here based on scope!

    # function call: name, args (None or a single value for now)
    [name, arg] = call
    if name == 'write':
        # arg is a list
        if arg:
            # not an empty list
            [_type, val] = arg
            if _type == 'literal':
                address = literal_table[val]
                code_section.append(f'OUT 0000 {address}')  # again, formatting
            else:
                code_section.append(f'OUT 0000 {val}')  # the name of the identifier exists in the assembly
    elif name == 'read':
        code_section.append('IN ???? 0000')  # just a random destination? or remember address of the assignee?
                              # there might not even be an assignee
    else:
        # appropriate action with parameters needs to be taken here
        code_section.append(f'CALL {name}')

def create_function_def(func: list):
    global function_section

    # handle args if necessary here
    [name, args, return_type, body] = func
    function_section.append(f'FUNC.{name}')
    [traverse(elt) for elt in body]
    # handle return

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
    # assign, return, arithmetic

    asm = ''
    for line in data_section:
        asm += line+'\n'
    for line in code_section:
        asm += line+'\n'
    asm += 'HLT 0000 0000\n'
    ##
    asm += '\nINPUT.SECTION\n'
    return asm

def main():
    pass

if __name__ == '__main__':
    global literal_table

    sample_ast = []  # to be gotten from static semantics
    
    '''
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
    4.hlpl: 
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
    '''
    with open('../milestone3/lex_output/literal_table.json') as f:
        literal_table = json.load(f)

    asm = traverse(sample_ast)
    print(asm)
