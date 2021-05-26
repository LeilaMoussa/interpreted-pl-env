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

    print('in call......')

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
        input_count += 1
        line = 'IN ???? 0000'
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
                # literal or operation
                # requires preceding assembly instructions and saving in memory
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
        # idk
        function_code_section.append('HLT 0000 0000')

def create_assign(assign: list):
    global input_count

    print('in assign......')
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
                # why bother call traverse here if the result is so easy to get like this? => not very elegant, but i can live with that
                line = f'IN {lhs} 0000'
                input_count += 1
            else:  # assuming the hlpl writer isn't crazy enough to use write, though that wouldn't be an issue for code generation
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

    # i'll implement these last 2 cases later
    if type(opd1) == list and type(opd2) == list:
        # it could be both of them or just one of them!
        # there will be traversing, but the tricky part here is that we're building an unfinished line
        line += 'stuff'
    else:
        # just userdefined ids or numeric literals
        # $$
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
    # the way we defined PUSH, the VALUE of the returnedExpression needs to be in the AC
    # easy for number values, but what about string/char literals?
    # we'd have to use an address
    # but how can we differentiate between
    # give a.  ==> ???? PUSH 0000 0000; HLT 0000 0000
    # give 1.  ==> ADD +0001 0000; PUSH 0000 0000; HLT 0000 0000 (add to put it on the AC)
    # give +(a, b) ==> ADD a b; PUSH 0000 0000; HLT...
    # give "yes". ==> ????
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
    # jump address is determined by the start of then_stats from create_selection
    line += 'xxxx '  # can't know jump address yet (label)
    if comp1.isnumeric():
        val = int(comp1)
        sign = '+' if val >= 0 else '-'
        val = str(val).rjust(4, "0")
        comp1 = sign + val
    line += comp1
    append_to_code(line)

def create_selection(select: list):
    # condition is eq ==> JMPE
    # condition is gt ==> JMPGE (yes, it's okay, GTE can encompass GT)
    [condition, then_stats, else_stats] = select
    create_test(condition)
    # then else_stats go here
    [traverse(elt) for elt in else_stats]
    # best i can do right now is end the program at the end of the selection
    # so a HLT comes after both blocks of stats (sorry)
    halt = 'HLT 0000 0000'
    append_to_code(halt)
    append_to_code('then')  # mark lines to determine jump line number, will be replaced by label
    [traverse(elt) for elt in then_stats]
    # line at which then_stats starts is the jump address, can't be known at the time condition is being created
    # so i'll put it there when asm is being built, at the end of traverse()

def create_loop(loop: list):
    [[_, [comp1, comp2]], stats] = loop
    append_to_code('LBL 0000 yyyy')
    # i need to make sure all labels across the whole code (loops and selections) don't repeat
    # structure: label, body, loop instruction
    # condition can be eq or gt
    # but LOOP keeps going while AC < upper bound
    # so let's only handle GT in conditions, and i'll assume that's all there is
    # comp1 is upperbound
    # need to keep putting value of comp2 in AC at the beginning of the loop
    if comp2.isnumeric():
        val = int(comp2)
        sign = '+' if val >= 0 else '-'
        comp2 = f'{sign}{comp2.rjust(4, "0")}'
    # i'm aware that this code needs to be put in a function
    append_to_code(f'ADD +0000 {comp2}')
    [traverse(elt) for elt in stats]
    if comp1.isnumeric():
        val = int(comp1)
        sign = '+' if val >= 0 else '-'
        comp1 = f'{sign}{comp1.rjust(4, "0")}'
    append_to_code(f'LOOP {comp1} yyyy')
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
    for line in entry_code_section:
        if line == 'then':
            label_count += 1
            label = 'L' + str(label_count)
            line = 'LBL 0000 ' + label
            asm = asm.replace('xxxx', label)
            print('just replaced')
        elif 'yyyy' in line:
            if line[:3] == 'LBL':
                label_count += 1
                label = 'L' + str(label_count)
            line = line.replace('yyyy', label)
        asm += line + '\n'
    asm += 'HLT 0000 0000\n'
    for line in function_code_section:
        # in theory, i need to do the same protocol for selection & loop labels here
        # but it's not a priority
        asm += line + '\n'
    asm += 'INPUT.SECTION\n'
    for _ in range(input_count):
        asm += '0 0 0000 0123\n'
    return asm

def test(asm: str, prog: str) -> bool:
    # changes to accommodate these expectations: no more PUSH or POP
    # and just CALL & RETURN instead
    # name capitalization/truncation if necessary
    # HLT in the case of non-give function termination
    # do we even need input.section, when we can implement it as a scanf() in the interpreter?
    # because otherwise, we'd have to come up with input here
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
    global literal_table, symbol_table

    ast = analyze(filepath, default, from_parser, from_analyzer, from_generator)
    print('ast given to generator:', ast)

    with open('../milestone3/lex_output/literal_table.json') as f:
        literal_table = json.load(f)
    with open('../milestone3/lex_output/symbol_table.json') as f:
        symbol_table = json.load(f)

    traverse(ast)
    asm = build_asm()
    print('----ASSEMBLY----')
    print(asm)
    prog_number = 'default'
    if filepath:
        prog_number = filepath.split('.hlpl')[0].split('/')[-1]  # Unix-style path.
    if not test(asm, prog_number):
        sys.exit('Generated assembly was not expected.')
    with open(f'./assembly/{prog_number}.asbl', 'w') as op:
        op.write(asm)

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        print('No HLPL input file provided for code generation,\
        proceeding with default code from milestone3/constants.py.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default, from_parser=True, from_analyzer=True, from_generator=True)

