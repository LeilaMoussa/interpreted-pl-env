'''
Sample IO:

In[1]: Program(Fix(num, a, 1), Entry(Var(num, b), Call(write, "hello")))
// Alternative representation with benefit of simple iteration:
// [Program, [Fix, [num, a, 1]], [Entry, [Var, [num, b]], [Call, [write, hello]]]]
Out[1]:
DATA.SECTION
DEC a 0001  // we need to show that it's (1) global, and (2) constant
DEC b 0000  // var is 0 by default, but we need to show that (1) it's var and (2) it's inside entry
// suggestion: DEC is redundant under DATA.SECTION, so maybe replace it by the name of the scope
CODE.SECTION
// instruction to delimit entry
// would be great if "hello" was replaced by its address from the literal table at the level of the SSA
OUT 0000 <address>
// instruction for end of entry?
HLT 0000 0000

//another suggestion
GLOBAL
// global vars, consts, and function definition base addresses
FUNC.START
// identify some function with its name or address
DATA.SECTION
// the function's local variables
CODE.SECTION
// its code
FUNC.START
// some other function, same thing
...
ENTRY
// same organization as func: data and code
// code for entry, this is what gets loaded into code memory at first
INPUT
// input data as usual
!!! THIS IS A BAD SUGGESTION because it changes our AL design too much !!!

// a third suggestion
DATA.SECTION
GLOB A 0001   // global var/const (we can ignore the var-const distinction for now)
DEF FUNC 0080  // function definition base address in CODE MEMORY
// BIG QUESTION: distinguish between declarations of different functions: do we have to?
CODE.SECTION
// code in entry
CALL FUNC   // call function, i.e. jump to base address, here 0080 in CODE MEMORY
// BUT BIGGEST QUESTION: where to write the AL for function body?
// One suggestion would be to write the definition inline, 
// so we need to delimit the start and end of the function somehow.
// limitation => it would be stupid to keep writing it inline for multiple calls to the same function


In[2]: [Program, [Func, [greet, None, None, Body, [Call, [write, "greetings"]]]], 
        [Entry, [Call, [greet, None]]]]
// the None's help, but are they suitable for an AST?
Out[2]:
idk honestly
helpful fact: we're only implementing functions with 0 or 1 params

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

'''

def traverse(ast: list):
    for elt in ast:
        # 2 cases: elt contains only terminals
        # -> leaves of the subtree whose root is the first element of elt in the previous iteration
        # OR elt contains at least one list
        # -> elt[0] is the root of at least one subtree
        # distinguish between roots with a deterministic number of leaves
        # and roots with a variable number of subtrees

        # all declarations are at the top of the AL code => need to keep track, 
        # i.e. don't write AL during traversal

        pass


if __name__ == '__main__':
    sample_ast = ['Program', ['Fix', ['num', 'a', 1]], ['Entry', ['Var', ['num', 'b']], 
                ['Call', ['write', 3]]]]  # assuming "hello" resides in data loc 0003

    traverse(sample_ast)