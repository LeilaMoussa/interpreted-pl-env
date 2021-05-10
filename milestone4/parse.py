import sys
import os
sys.path.append(os.path.abspath('../milestone3'))
from lex import main as generate

VERBOSE = True

token_gen = None  # token_gen is a generator object of (token, lexeme, line_number)
current_token = None
line = -1
position = -1

def get_next_token():
    global token_gen, line, position
    try:
        token_info = token_gen.__next__()
        print("getting next token")
        line += 1
        position += 1
        return token_info[0]
        # first element of the tuple is the token, but we might also need the lexeme for the tree
    except:
        sys.exit("Reached end of token stream with no errors!")

def program():
    global current_token
    if VERBOSE: print("In program.")
    local_position = position
    while declaration():
        pass
    if position > local_position: return False
    local_position = position
    while function():
        pass
    if position > local_position: return False
    # We need to handle the possibility of bad syntax of functions
    # i.e. progress being made, so they're definitely functions (or declarations)
    # but they have wrong syntax => raise error, don't just pass
    # I think we can achieve this easily with a position counter for the token
    # same for everything with while
    if not mainFunction():
        return False
    return True
        
def declaration():
    global current_token
    if VERBOSE: print("In declaration.")
    if not varDeclaration():
        if not fixDeclaration():
            return False
    if current_token != 'ENDSTAT':
        return False
    current_token = get_next_token()   # this isn't the function's responsibility, but anyway
    return True

def varDeclaration():
    global current_token
    if VERBOSE: print("In varDeclaration.")
    if current_token != 'VAR_KW':
        return False
    current_token = get_next_token()
    if not typeSpecifier():
        return False
    if not userDefinedIentifier():
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
        pass
    if position > local_position: return False
    local_position = position
    while statement() or function():
        pass
    if position > local_position: return False
    if current_token != 'RBRACK':
        return False
    current_token = get_next_token()
    return True

def size():
    if VERBOSE: print("In size.")
    if not userDefinedIdentifier():
        if not digit():
            return False
        else:
            while digit():
                pass
    # !! we don't deal with digits anymore, just numeric literals!
    return True

def function():
    # rule for function definition, starting with func
    global current_token
    if VERBOSE: print("In function.")
    if current_token != 'FUNC_KW':
        print("wtff")
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
        pass
    if position > local_position: return False
    local_position = position
    while statement():
        pass
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
        pass
    if position > local_position: return False
    local_position = position
    while statement():
        pass
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
        pass
    if position > local_position: return False
    local_position = position
    while statement() or function():
        pass
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
        pass
    if position > local_position: return False
    local_position = position
    while statement():
        pass
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
    print("token is now", current_token)
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
    return True

def numericLiteral():
    global current_token
    if VERBOSE: print("In numericLiteral.")
    if current_token != 'NUM_LIT':
        return False
    current_token = get_next_token()
    return True

def main(filepath, default, from_parser):
    global token_gen, current_token
    token_gen = generate(filepath, default, from_parser)
    current_token = get_next_token()
    # for elt in token_gen:
    #     print(elt)
    if not program():
        print("Error occured. Read error messages.")

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        print('No HLPL input file provided for parsing, proceeding with default code.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default, from_parser=True)
