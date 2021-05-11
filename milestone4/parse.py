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
        sys.exit("All tokens consumed!")  # i haven't handled the case of a program with no mainFunction yet... idk how right now

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
    main_node = mainFunction()
    if not main_node:   # either MainNode() or None, so i guess everyone's return values should change to either ASTNode() instance or None
        # keeping False would be fine because None and False are both treated the same!
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
    if not typeSpecifier():
        return False
    if not userDefinedIdentifier():
        return False
    return True

def fixDeclaration() -> bool:
    global current_token
    if VERBOSE: print("In fixDeclaration.")
    if current_token != 'CONST_KW':
        return False
    current_token = get_next_token()
    if not typeSpecifier():
        return False
    if not userDefinedIdentifier():
        return False
    if current_token != 'ASGN':
        return False
    current_token = get_next_token()
    if not expression():
        if not operation():
            if not functionCall():
                return False
    return True

def typeSpecifier():
    global current_token
    if VERBOSE: print("In typeSpecifier.")
    if current_token != 'NUM_KW':
        if current_token != 'CHAR_KW':
            if current_token != 'NUM_ADDR_KW':
                if current_token != 'CHAR_ADDR_KW':
                    return False
    #Still need to add arrays and strings, I guess no need for the moment
    #you consumed a token now, get next one
    current_token = get_next_token()
    return True

def userDefinedIdentifier():
    #doesn't handle indexing yet
    global current_token
    if VERBOSE: print("In userDefinedIdentifier.")
    if current_token != 'IDENT':
        return False
    current_token = get_next_token()
    return True

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
    # so put the following in another function
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

def size():
    if VERBOSE: print("In size.")
    if not userDefinedIdentifier():
        if current_token != 'NUM_LIT':
            return False
        # they need to be positive, so look at lexeme[0] => clunky, but necessary
        # because the token is a NUM_LIT
    return True

def function():
    # rule for function definition, starting with func
    global current_token
    if VERBOSE: print("In function.")
    if current_token != 'FUNC_KW':
        return False
    current_token = get_next_token()
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    if not parameter():
        # !! we need to support 0 params
        return False
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'ARROW':
        return False
    current_token = get_next_token()
    if not userDefinedIdentifier():
        return False
    if current_token != 'ARROW':
        return False
    current_token = get_next_token()
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    if not typeSpecifier():
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
    return True
    
def parameter():
    global current_token
    if VERBOSE: print("In parameter.")
    if not typeSpecifier():
        return False
    if not identifier():
        return False
    #Still need to handle multiple parameters, will do later
    return True

def statement():
    global current_token
    if VERBOSE: print("In statement.")
    if not assignment():
        if not returnStatement():
            if not selection():
                if not loop():
                    if not functionCall():
                        return False
    current_token = get_next_token()
    return True
            
def assignment():
    global current_token
    if VERBOSE: print("In assignment.")
    if not userDefinedIdentifier():
        return False
    if current_token != 'ASGN':
        return False
    current_token = get_next_token()
    if not expression():
        if not operation():
            if not functionCall():
                return False
    if current_token != 'ENDSTAT':
        return False
    current_token = get_next_token()
    return True

def returnStatement():
    global current_token
    if VERBOSE: print("In returnStatement.")
    if current_token != 'RETURN_KW':
        return False
    current_token = get_next_token()
    if not returnedExpression():
        return False
    if current_token != 'ENDSTAT':
        return False
    current_token = get_next_token()
    return True

def returnedExpression():
    if VERBOSE: print("In returnedExpression.")
    if not expression():
        if not functionCall():
            return False
    return True

def selection():
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
    if current_token != 'ADD':
        if current_token != 'SUB':
            if current_token != 'MULT':
                if current_token != 'DIV':
                    return False
    current_token = get_next_token()
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    if not operand():
        return False
    if current_token != 'COMMA':
        return False
    current_token = get_next_token()
    if not operand():
        return False
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'ENDSTAT':
        return False
    current_token = get_next_token()
    return True

def operand():
    if VERBOSE: print("In operand.")
    if not numericLiteral():
        if not userDefinedIdentifier():
            if not operation():
                if not functionCall():
                    return False
    return True

def functionCall():
    global current_token
    if VERBOSE: print("In functionCall.")
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    if not expression():
        return False
    #only handling function calls with 1 parameter for the time being
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'ARROW':
        return False
    current_token = get_next_token()
    if not identifier():
        return False
    if current_token != 'ENDSTAT':
        return False
    current_token = get_next_token()
    return True

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
    if current_token == 'CHAR_LIT' or current_token == 'STR_LIT':
        current_token = get_next_token()
        return True
    if not numericLiteral():
        if not userDefinedIdentifier():
            return False
    return True
            
def identifier():
    if VERBOSE: print("In identifier.")
    if not userDefinedIdentifier():
        if not reservedWord():
            return False
    return True

def reservedWord():
    global current_token
    if VERBOSE: print("In reservedWord.")
    if current_token != 'IN_KW' and current_token != 'OUT_KW':
        return False
    current_token = get_next_token()
    return ReservedNode(current_token)   # actually should be current_lexeme, will probably add a global variable for lexeme

def numericLiteral():
    global current_token
    if VERBOSE: print("In numericLiteral.")
    if current_token != 'NUM_LIT':
        return False
    current_token = get_next_token()
    return True  # NumLiteralNode(current_lexeme)

######################################################################

def main(filepath, default, from_parser):
    global token_gen, current_token
    token_gen = generate(filepath, default, from_parser)
    current_token = get_next_token()
    # for elt in token_gen:
    #     print(elt)
    if not program():  # eventually, program() returns the whole CST
        print("Error occured. Read error messages.")
    # since we'll run the parser from the static semantics analyzer, we'll obtain the CST directly at that level
    # AST will not necessarily have the same representation
    # we can go for something else like nested list/ dict, whatever is easier to construct
    # again, static semantics analyzer will be run from the generator
    # so end2end running will have 3 steps: 1. run generator 2. run assembler 3. run interpreter

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        print('No HLPL input file provided for parsing, proceeding with default code.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default, from_parser=True)
