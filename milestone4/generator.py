'''
Sample IO:

In[1]: Program(Fix(num, a, 1), Entry(Var(num, b), Call(write, "hello")))
// Alternative representation with benefit of simple iteration:
// [Program, [Fix, [num, a, 1]], [Entry, [Var, [num, b]], [Call, [write, hello]]]]
Out[1]:
DATA.SECTION
GLOB a 0001
ENTR b 0000
CODE.SECTION
// i think literal table contents need to be loaded into memory before program execution
OUT 0000 <address>
HLT 0000 0000

In[2]: [Program, [Func, [greet, None, None, Body, [Call, [write, "greetings"]]]], 
        [Entry, [Call, [greet, None]]]]
// the None's help, but are they suitable for an AST?
Out[2]:
DATA.SECTION
CODE.SECTION
CALL GREET 0000
HLT 0000 0000
FUNC.GREET
OUT 0000 <address>
HLT 0000 0000

In[3]: [Program, 
            [Func, 
                [adder, 
                    [[num, a], [num, b]], // args
                    num,                  // return type
                    Body, [              // body, doesn't necessarily need Body tag IF WE USE None
                            [Var, [num, result]],
                            [Assign, [result, plus, [a, b]]],
                            [Give, result]
                          ]
                ]
            ], // end func
            [Entry, [Var, [num, a]],
                    [Var, [num, b]],
                    [Call, 
                        [write, [Call, 
                                    [adder,   // func name
                                    [a, b]]]] // given arguments
                    ]
            ]  // end entry
        ]  // end prog
Out[3]:
DATA.SECTION
ENTR A 0000
ENTR B 0000
FUNC RESULT 0000
CODE.SECTION
MOV A 0010
MOV B 0011
CALL ADDER 0000
OUT <????>  // idk??
HLT 0000 0000
FUNC.ADDER
// how to treat local variables
// add
// move
// return: put result in memory location agreed upon by entry
'''
import json

data_section = ['DATA.SECTION', ]
code_section = ['CODE.SECTION', ]
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

def traverse(ast: list):
    global scope

    for i, elt in enumerate(ast):  # loop, really?
        if elt == 'program':
            scope = 'GLOB'
            [traverse(item) for item in ast[i:]]
        elif elt == 'entry':
            scope = 'ENTR'
            [traverse(item) for item in ast[i:]]
        elif elt == 'func':
            scope = 'FUNC'
        elif elt == 'fix' or elt == 'var':
            create_dec(ast[i+1], scope)
        elif elt == 'call':
            create_call(ast[i+1])
    asm = ''
    for line in data_section:
        asm += line+'\n'
    for line in code_section:
        asm += line+'\n'
    asm += 'HLT 0000 0000\nINPUT.SECTION\n'
    return asm

if __name__ == '__main__':
    global literal_table

    # tbh, we don't even need types or fix/var anymore
    sample_ast = ['program', ['fix', ['num', 'a', 1]], ['entry', ['var', ['num', 'b']], 
                ['call', ['write', ['literal', '"hello"']]]]]
    # super important to get strings written this way
    '''
    DATA.SECTION
    GLOB a 0001
    ENTR b 0000
    CODE.SECTION
    OUT 0000 0003  // assuming address of 'hello' is 0003
    HLT 0000 0000
    '''
    with open('../milestone3/lex_output/literal_table.json') as f:
        literal_table = json.load(f)

    asm = traverse(sample_ast)
    print(asm)
