from milestone4.cst import OperationNode
import sys
import os
sys.path.append(os.path.abspath('../milestone3'))
from lex import main as generate
from cst import *

VERBOSE = True

token_gen = None  # token_gen is a generator object of (token, lexeme, line_number)
current_token = None
lexeme = ''
line = -1   # would like to use this for error messages, but not necessary
position = -1

def get_next_token():
    global token_gen, line, position, lexeme
    try:
        token_info = token_gen.__next__()
        position += 1
        (token, lexeme, line) = token_info
        if VERBOSE: print("Current token:", token)
        return token
    except:
        print('exhausted')
        return None

def program():
    global current_token
    if VERBOSE: print("In program.")
    local_position = position
    dec_nodes = []
    while node := declaration():
        local_position = position
        dec_nodes.append(node)
    if position > local_position: return False  # by virtue of LL(1)
    func_nodes = []
    while node := function():
        local_position = position
        func_nodes.append(node)
    if position > local_position: return False
    if not current_token: return False
    main_node = mainFunction()
    if not main_node:
        return False
    return ProgramNode(dec_nodes, func_nodes, main_node)  # instead of True
        
def declaration():
    global current_token
    if VERBOSE: print("In declaration.")
    var_node = varDeclaration()
    fix_node = None
    if not var_node:
        fix_node = fixDeclaration()
        if not fix_node:
            return False
    if current_token != 'ENDSTAT':
        return False
    current_token = get_next_token()
    return DeclarationNode(var_node, fix_node)

def varDeclaration():
    global current_token
    if VERBOSE: print("In varDeclaration.")
    if current_token != 'VAR_KW':
        return False
    current_token = get_next_token()
    if not current_token: return False
    type_node = typeSpecifier()
    if not type_node:
        return False
    if not current_token: return False
    udi_node = userDefinedIdentifier()
    if not udi_node:
        return False
    return VarDeclarationNode(type_node, udi_node)

def fixDeclaration() -> bool:
    global current_token
    if VERBOSE: print("In fixDeclaration.")
    if current_token != 'CONST_KW':
        return False
    current_token = get_next_token()
    if not current_token: return False
    type_node = typeSpecifier()
    if not type_node:
        return False
    if not current_token: return False
    udi_node = userDefinedIdentifier()
    if not udi_node:
        return False
    if current_token != 'ASGN':
        return False
    current_token = get_next_token()
    if not current_token: return False
    exp_node = expression()
    op_node = call_node = None
    if not exp_node:
        op_node = operation()
        if not op_node:
            call_node = functionCall()
            if not call_node:
                return False
    current_token = get_next_token()
    return FixDeclarationNode(type_node, udi_node, exp_node, op_node, call_node)

def typeSpecifier():
    global current_token
    if VERBOSE: print("In typeSpecifier.")
    if current_token != 'NUM_KW':
        if current_token != 'CHAR_KW':
            if current_token != 'NUM_ADDR_KW':
                if current_token != 'CHAR_ADDR_KW':
                    return False
    local_lexeme = lexeme
    current_token = get_next_token()
    return TypeNode(local_lexeme)

def userDefinedIdentifier():
    # won't do indexing
    global current_token
    if VERBOSE: print("In userDefinedIdentifier.")
    if current_token != 'IDENT':
        return False
    local_lexeme = lexeme
    current_token = get_next_token()
    return UserDefinedNode(local_lexeme)

def mainFunction():
    global current_token
    if VERBOSE: print("In mainFunction.")
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'ARROW':
        return False
    current_token = get_next_token()
    if current_token != 'MAIN_KW':
        return False
    current_token = get_next_token()
    if current_token != 'ARROW':
        return False
    current_token = get_next_token()
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'LBRACK':
        return False
    # i think beyond here, `mainFunction` and `function` have the same body
    # so put the following in another function (not sure about this suggestion yet)
    current_token = get_next_token()
    if not current_token: return False
    local_position = position
    decs = []
    while node := declaration():
        decs.append(node)
        local_position = position
    if position > local_position: return False
    stats = []
    while True:
        if node := statement():
            stats.append(node)
            print('appended node to stats in main')
        elif node := function():  # we can forget about nested functions for now
            pass
        else:
            break
        local_position = position
    if position > local_position: return False
    print('current', current_token)
    if current_token != 'RBRACK':
        print("hi")
        return False
    current_token = get_next_token()
    return MainNode(decs, stats)

def size():
    # we probably won't use strings/arrays, so forget about this guy
    if VERBOSE: print("In size.")
    if not userDefinedIdentifier():
        if current_token != 'NUM_LIT':
            return False
        # they need to be positive, so look at lexeme[0] => clunky, but necessary
        # because the token is a NUM_LIT
    return True

def function():
    # rule for function definition
    global current_token
    if VERBOSE: print("In function.")
    if current_token != 'FUNC_KW':
        return False
    current_token = get_next_token()
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    args = []
    if node := parameter():
        args.append(node)
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'ARROW':
        return False
    current_token = get_next_token()
    if not current_token: return False
    udi_node = userDefinedIdentifier()
    if not udi_node:
        return False
    if current_token != 'ARROW':
        return False
    current_token = get_next_token()
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    if not current_token: return False
    type_node = typeSpecifier()  # return type
    # could be None or False if function doesn't return anything
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'LBRACK':
        return False
    current_token = get_next_token()
    local_position = position
    decs = []
    while node := declaration():
        decs.append(node)
        local_position = position
    if position > local_position: return False
    stats = []
    while node := statement():
        stats.append(node)
        local_position = position
    if position > local_position: return False
    if current_token != 'RBRACK':
        return False
    return FunctionNode(udi_node, args, type_node, decs, stats)
    
def parameter():
    global current_token
    if VERBOSE: print("In parameter.")
    if not current_token: return False
    type_node = typeSpecifier()
    if not type_node:
        return False
    if not current_token: return False
    udi_node = userDefinedIdentifier()
    if not udi_node:
        return False
    return ParamNode(type_node, udi_node)

def statement():
    global current_token
    if VERBOSE: print("In statement.")
    if not current_token:
        print('mmmmmmmm')
        return False
    a_node = assignment()
    r_node = s_node = l_node = f_node = None
    if not a_node:
        r_node = returnStatement()
        if not r_node:
            s_node = selection()
            if not s_node:
                l_node = loop()
                if not l_node:
                    f_node = functionCall()
                    print('made a call node')
                    if not f_node:
                        return False
    # current_token = get_next_token()
    return StatementNode(a_node, r_node, s_node, l_node, f_node)
            
def assignment():
    global current_token
    if VERBOSE: print("In assignment.")
    if not current_token: return False
    udi_node = userDefinedIdentifier()
    if not udi_node:
        return False
    if current_token != 'ASGN':
        return False
    current_token = get_next_token()
    if not current_token: return False
    exp_node = expression()
    op_node = call_node = None
    if not exp_node:
        op_node = operation()
        if not op_node:
            call_node = functionCall()
            if not call_node:
                return False
    if current_token != 'ENDSTAT':
        return False
    current_token = get_next_token()
    return AssignmentNode(udi_node, exp_node, op_node, call_node)

def returnStatement():
    global current_token
    if VERBOSE: print("In returnStatement.")
    if current_token != 'RETURN_KW':
        return False
    current_token = get_next_token()
    if not current_token: return False
    exp_node = expression()
    call_node = None
    if not exp_node:
        call_node = functionCall()
        if not call_node:
            return False
    if current_token != 'ENDSTAT':
        return False
    current_token = get_next_token()
    return ReturnNode(exp_node, call_node)

def selection():
    # still not handled for the CST!
    global current_token
    if VERBOSE: print("In selection.")
    if current_token != 'IF_KW':
        return False
    current_token = get_next_token()
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    if not conditionStatement():
        return False
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'LBRACK':
        return False
    current_token = get_next_token()
    local_position = position
    while declaration():
        local_position = position
    if position > local_position: return False
    while statement():
        local_position = position
    if position > local_position: return False
    if current_token != 'RBRACK':
        return False
    current_token = get_next_token()
    if current_token != 'ELSE_KW':
        return False
    current_token = get_next_token()
    if current_token != 'LBRACK':
        return False
    current_token = get_next_token()
    local_position = position
    while declaration():
        local_position = position
    if position > local_position: return False
    while statement() or function():
        local_position = position
    if position > local_position: return False
    if current_token != 'RBRACK':
        return False
    current_token = get_next_token()
    return True
    
def loop():
    global current_token
    if VERBOSE: print("In loop.")
    if current_token != 'LOOP_KW':
        return False
    current_token = get_next_token()
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    if not conditionStatement():
        return False
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'LBRACK':
        return False
    current_token = get_next_token()
    local_position = position
    while declaration():
        local_position = position
    if position > local_position: return False
    while statement():
        local_position = position
    if position > local_position: return False
    if current_token != 'RBRACK':
        return False
    current_token = get_next_token()
    return True

def operation():
    global current_token
    if VERBOSE: print("In operation.")
    op = None
    if current_token == 'ADD':
        op = 1
    elif current_token == 'SUB':
        op = 2
    elif current_token == 'MULT':
        op = 3
    elif current_token == 'DIV':
        op = 4
    else:
        return False
    current_token = get_next_token()
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    opd1_node = operand()
    if not opd1_node:
        return False
    if current_token != 'COMMA':
        return False
    current_token = get_next_token()
    opd2_node = operand()
    if not opd2_node:
        return False
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'ENDSTAT':
        return False
    current_token = get_next_token()
    return OperationNode(op, opd1_node, opd2_node)

def operand():
    if VERBOSE: print("In operand.")
    n_node = numericLiteral()
    uid_node = op_node = call_node = None
    if not n_node:
        uid_node = userDefinedIdentifier()
        if not uid_node:
            op_node = operation()
            if not op_node:
                call_node = functionCall()
                if not call_node:
                    return False
    return OperandNode(n_node, uid_node, op_node, call_node)

def functionCall():
    # let's try to handle 0 params, but not more than one
    global current_token
    if VERBOSE: print("In functionCall.")
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    args = []
    if node := expression():  # if we wanted to handle multiple params, this would be a while
        args.append(node)
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'ARROW':
        return False
    current_token = get_next_token()
    if not current_token: return False
    name = identifier()
    if not name:
        return False
    if current_token != 'ENDSTAT':
        return False
    current_token = get_next_token()
    return CallNode(name, args)

def conditionStatement():
    #only handling single comparisons without a 'not' for the time being
    global current_token
    if VERBOSE: print("In conditionStatement.")
    if not comparison():
        return False
    #more work needs to be done here
    return True

def comparison():
    global current_token
    if VERBOSE: print("In comparison.")
    if current_token != 'EQ' and current_token != 'GT':
        return False
    current_token = get_next_token()
    if current_token != 'LPAREN':
        return False
    if not compared():
        return False
    if not compared():
        return False
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    return True

def compared():
    if VERBOSE: print("In compared.")
    if not numericLiteral():
        if not userDefinedIdentifier():
            if not functionCall():
                return False
    return True

def expression():
    global current_token
    if VERBOSE: print("In expression.")
    char_node = str_node = num_node = udi_node = None
    if current_token == 'CHAR_LIT':
        char_node = CharLiteralNode(lexeme)
        current_token = get_next_token()
    elif current_token == 'STR_LIT':
        str_node = StringLiteralNode(lexeme)
        current_token = get_next_token()
    elif current_token == 'NUM_LIT':
        num_node = NumLiteralNode(int(lexeme))
    elif udi_node := userDefinedIdentifier():
        pass
    else:  # none of these 4, or None
        return False
    return ExpressionNode(char_node, str_node, num_node, udi_node)
            
def identifier():
    if VERBOSE: print("In identifier.")
    if not current_token: return False
    udi_node = userDefinedIdentifier()
    res_node = None
    if not udi_node:
        res_node = reservedWord()
        if not res_node:
            return False
    return IdentifierNode(udi_node, res_node)

def reservedWord():
    global current_token
    if VERBOSE: print("In reservedWord.")
    if current_token != 'IN_KW' and current_token != 'OUT_KW':
        return False
    local_lexeme = lexeme
    current_token = get_next_token()
    return ReservedNode(local_lexeme)

def numericLiteral():
    global current_token
    if VERBOSE: print("In numericLiteral.")
    if current_token != 'NUM_LIT':
        return False
    current_token = get_next_token()
    return NumLiteralNode(lexeme)

######################################################################

def main(filepath, default, from_parser, from_analyzer=False):
    global token_gen, current_token
    token_gen = generate(filepath, default, from_parser)
    current_token = get_next_token()
    parse_tree = program()
    if parse_tree:
        if from_analyzer: return parse_tree
        print('displaying parse tree...')
        parse_tree.display()
    else:
        print('Error.')

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        print('No HLPL input file provided for parsing, proceeding with default code \
            from milestone3/constants.py.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default, from_parser=True)
