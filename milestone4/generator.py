import json, sys
from static_semantics_analyzer import main as analyze

data_section = ['DATA.SECTION', ]
entry_code_section = ['CODE.SECTION', ]
function_code_section = []
scope = None
input_count = 0

def append_to_code(line: str):
    if scope == 'ENTR': entry_code_section.append(line)
    elif scope == 'FUNC': function_code_section.append(line)

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
    global input_count

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
        # I guess data location 5000 is very unlikely to be occupied...
        input_count += 1
        line = 'IN [5000] 0000'
    else:
        # function with no params: CALL <name> 0000
        # one param: CALL <name> <param as symbol or numeric literal or address>
        line = f'CALL {name.upper()} '
        if len(args) == 0:
            line += '0000'
        else:
            # arguments are expressions
            arg = args[0]
            # again, we're only implementing one argument on purpose, 
            # though theoretically it would be pretty easy to accommodate any number
            if type(arg) == list:
                kind = arg[0]
                if kind == 'literal':
                    line += literal_table[arg[1]].rjust(4, "0")
                else:
                    # operation, we decided not to do this
                    pass
            else:
                # udi
                line += arg  # identifier name
    append_to_code(line)

def create_function_def(func: list):
    [name, _, _, body] = func  # anon: args & return_type
    function_code_section.append(f'FUNC.{name.upper()}')
    [traverse(elt) for elt in body]
    last_written = function_code_section[-1]
    if last_written != 'HLT 0000 0000' and last_written != 'RETURN 0000 0000':
        function_code_section.append('HLT 0000 0000')

def create_assign(assign: list):
    global input_count

    [lhs, rhs] = assign
    line = ''
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
                literal = str(literal).rjust(4, "0")
                line = f'MOV {lhs} {sign}{literal}'  # padding
            else:
                line = f'MOV {lhs} [{literal_table[literal]}]'  # padding
        elif root == 'funcall':
            # read, write, or userdefined function
            # 1. read:  IN <lhs> 0000
            # 2. write: shouldn't happen because it makes no sense, so won't bother writing the expected result
            # 3. userdefined: CALL, POP, MOVAC (remember, MOVAC means move OUT of the AC)
            if body[0] == 'read':
                # why bother call traverse here if the result is so easy to get like this?
                #  => not very elegant, but we can live with that
                line = f'IN {lhs} 0000'
                input_count += 1
            else:
                # assuming the hlpl writer isn't crazy enough to use write, though that wouldn't be an issue for code generation
                traverse(rhs)
                pop = 'POP 0000 0000'  # to use the return value, put in AC
                movac = f'MOVAC {lhs} 0000'  # put return value in LHS
                append_to_code(pop)
                append_to_code(movac)
        else:
            # arithmetic
            [op, opds] = rhs
            if op == 'add': op = 1
            elif op == 'sub': op = 2
            elif op == 'mult': op = 3
            elif op == 'div': op = 4
            create_arithmetic(op, opds)
            line = f'MOVAC {lhs} 0000'
    else:
        # rhs is udi
        line = f'MOV {lhs} {rhs}'
    append_to_code(line)

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

    if type(opd1) == list and type(opd2) == list:
        # function calls or operations
        # it could be both of them or just one of them!
        # there will be traversing, but the tricky part here is that we're building an unfinished line
        # unimplemented, unfortunately
        pass
    else:
        # just userdefined ids or numeric literals
        # We recognize the sub-optimal code quality, sorry!
        if opd2.isnumeric():
            sign = '+' if int(opd2) >= 0 else '-'
            opd2 = sign + opd2.rjust(4, "0")
        if opd1.isnumeric():
            sign = '+' if int(opd1) >= 0 else '-'
            opd1 = sign + opd1.rjust(4, "0")
        line += f'{opd1} {opd2}'
    append_to_code(line)

def create_return(given: list):
    # given can be a userdefined id, an operation, a literal, or a function call
    # we decided to keep details away from the AL and push them over to the interpreter
    # where actual stack management should be implemented.
    # the alternative was to handle pushing return values here, but that has proven to be difficult
    # because we envisioned the stack as holding return addresses, parameters, and return values
    # and pushing a return value requires an empty stack
    # (this is a pretty nuanced discussion and we've been quite confused about it,
    # if you'd like to know more we can elaborate later)

    # In short: RETURN 0000 0000
    traverse(given)
    function_code_section.append('RETURN 0000 0000')

def create_test(condition: list):
    [operator, [comp1, comp2]] = condition
    line = ''
    if operator == 'eq':
        line += 'JMPE '
    elif operator == 'gt':
        line += 'JMPGE '
    # comparands can be numeric literals, identifiers, or function calls
    # let's ignore function calls right now, they're far too complicated 
    # (they involve CALL POP and potentially MOV)
    if comp2.isnumeric():
        val = int(comp2)
        sign = '+' if val >= 0 else '-'
        val = str(val).rjust(4, "0")
        to_add = sign + val
    else:
        to_add = comp2  # symbol
    to_ac = f'ADD +0000 {to_add}'
    append_to_code(to_ac)
    # jump address (label) is determined by the start of then_stats from create_selection
    line += 'xxxx '  # can't know jump address yet (label)
    if comp1.isnumeric():
        val = int(comp1)
        sign = '+' if val >= 0 else '-'
        val = str(val).rjust(4, "0")
        comp1 = sign + val
    line += comp1
    append_to_code(line)

def create_selection(select: list):
    [condition, then_stats, else_stats] = select
    create_test(condition)
    # condition can be eq or gt
    # else_stats go first
    [traverse(elt) for elt in else_stats]
    halt = 'HLT 0000 0000'
    append_to_code(halt)
    # Ending the code after the 'then' and 'else' clauses for simplicity.
    append_to_code('then')  # mark lines to determine jump line number, will be replaced by label in build_asm()
    [traverse(elt) for elt in then_stats]
    # line at which then_stats starts is the jump address (label), which 
    # can't be known at the time condition is being created
    # so i'll put it there when asm is being built in build_asm()

def create_loop(loop: list):
    [[_, [comp1, comp2]], stats] = loop
    append_to_code('LBL 0000 yyyy')
    # yyyy is the placeholder for loop labels, the same way xxxx is the placeholder for selection labels
    # with some small differences between the 2 (depends on where LBL is relative to JMP or LOOP)
    if comp2.isnumeric():
        val = int(comp2)
        sign = '+' if val >= 0 else '-'
        comp2 = f'{sign}{comp2.rjust(4, "0")}'
    append_to_code(f'ADD +0000 {comp2}')
    [traverse(elt) for elt in stats]
    if comp1.isnumeric():
        val = int(comp1)
        sign = '+' if val >= 0 else '-'
        comp1 = f'{sign}{comp1.rjust(4, "0")}'
    append_to_code(f'LOOP {comp1} yyyy')

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
        create_assign(ast[1])
    elif root == 'give':
        create_return(ast[1])
    elif root == 'add':
        create_arithmetic(1, ast[1])
    elif root == 'sub':
        create_arithmetic(2, ast[1])
    elif root == 'mult':
        create_arithmetic(3, ast[1])
    elif root == 'div':
        create_arithmetic(4, ast[1])
    elif root == 'loop':
        create_loop(ast[1])
    elif root == 'selection':
        create_selection(ast[1])

def build_asm():
    asm = ''
    for line in data_section:
        asm += line + '\n'
    label_count = 0
    # Sorry for the eye sore: the repeated code below takes care of resolving labels
    # such that JMPs refer to a label defined after them, and LOOPs refer to labels defined before them
    # in both the main function and the user defined function
    for line in entry_code_section:
        if line == 'then':
            label_count += 1
            label = 'L' + str(label_count)
            line = 'LBL 0000 ' + label
            asm = asm.replace('xxxx', label)
        elif 'yyyy' in line:
            if line[:3] == 'LBL':
                label_count += 1
                label = 'L' + str(label_count)
            line = line.replace('yyyy', label)
        asm += line + '\n'
    asm += 'HLT 0000 0000\n'
    for line in function_code_section:
        if line == 'then':
            label_count += 1
            label = 'L' + str(label_count)
            line = 'LBL 0000 ' + label
            asm = asm.replace('xxxx', label)
        elif 'yyyy' in line:
            if line[:3] == 'LBL':
                label_count += 1
                label = 'L' + str(label_count)
            line = line.replace('yyyy', label)
        asm += line + '\n'
    asm += 'INPUT.SECTION\n'
    for _ in range(input_count):
        # For programs using () => read. , i.e. reading user input,
        # we decided to provide dummy input at this level
        # type checking these reads is doable, but we didn't do it
        asm += '0 0 0000 0123\n'
    return asm

def test(asm: str, prog: str) -> bool:
    if prog == 'default':
        expect = '''DATA.SECTION
CODE.SECTION
HLT 0000 0000
INPUT.SECTION
'''
    elif prog == '1':
        expect = '''DATA.SECTION
GLOB a +0002
GLOB b +0000
CODE.SECTION
OUT 0000 [9998]
HLT 0000 0000
INPUT.SECTION
'''
    elif prog == '2':
        expect = '''DATA.SECTION
CODE.SECTION
CALL GREET 0000
HLT 0000 0000
FUNC.GREET
OUT 0000 [9999]
HLT 0000 0000
INPUT.SECTION
'''
    elif prog == '3':
        expect = '''DATA.SECTION
GLOB initial +0003
CODE.SECTION
CALL GREET 0000
HLT 0000 0000
FUNC.GREET
OUT 0000 [9998]
OUT 0000 initial
HLT 0000 0000
INPUT.SECTION
'''
    elif prog == '4':
        expect = '''DATA.SECTION
GLOB a +0010
ENTR b +0000
CODE.SECTION
IN b 0000
CALL PRODUCT b
HLT 0000 0000
FUNC.PRODUCT
MULT a b
RETURN 0000 0000
INPUT.SECTION
0 0 0000 0123
'''   # our dummy value is always 123
    elif prog == '5':
        expect = '''DATA.SECTION
CODE.SECTION
ADD +0000 +0002
JMPGE L1 +0001
OUT 0000 [9996]
HLT 0000 0000
LBL 0000 L1
OUT 0000 [9997]
HLT 0000 0000
INPUT.SECTION
'''
    elif prog == '6':
        expect = '''DATA.SECTION
ENTR i +0000
CODE.SECTION
MOV i +0000
LBL 0000 L1
ADD +0000 i
OUT 0000 [9997]
ADD i +0001
MOVAC i 0000
LOOP +0005 L1
HLT 0000 0000
INPUT.SECTION
'''
    else:
        return True
    return asm == expect

def main(filepath: str, default: bool, from_parser, from_analyzer, from_generator):
    global literal_table

    ast = analyze(filepath, default, from_parser, from_analyzer, from_generator)
    print('-------- AST: ---------')
    print(ast)

    with open('../milestone3/lex_output/literal_table.json') as f:
        literal_table = json.load(f)

    print('============================= START CODE GENERATION ==================================')
    traverse(ast)
    asm = build_asm()
    print('----ASSEMBLY----\n')
    print(asm)
    prog_number = 'default'
    if filepath:
        prog_number = filepath.split('.hlpl')[0].split('/')[-1]  # Unix-style path.
    if not test(asm, prog_number):
        sys.exit('Generated assembly was not expected.')
    else:
        print('Generated assembly matches expectations!')
    with open(f'./assembly/{prog_number}.asbl', 'w') as op:
        op.write(asm)

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        print('No HLPL input file provided for code generation, \
proceeding with default code from milestone3/constants.py.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default, from_parser=True, from_analyzer=True, from_generator=True)

