import sys
import os
sys.path.append(os.path.abspath('../milestone3'))
from lex import main as generate

VERBOSE = True

token_gen = None
current_token = None

def get_next_token():
    print("getting next token")
    try:
        return token_gen.__next__()
    except:
        sys.exit("Reached end of token stream!\n")

def program():
    global current_token
    if VERBOSE: print("In program.")
    while declaration():
        pass
    while function():
        pass
    if not mainFunction():
        return False 
        
def declaration():
    global current_token
    if VERBOSE: print("In declaration.")
    if not varDeclaration():
        if not fixDeclaration():
            return False
    if (current_token != 'ENDSTAT'):
        return False
    else:
        #all's good, consume next token
       current_token = get_next_token()

def varDeclaration():
    global current_token
    if VERBOSE: print("In varDeclaration.")
    if current_token != 'VAR_KW':
        return False
    else: 
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
    else:
       current_token = get_next_token()
    if not typeSpecifier():
        return False
    if not userDefinedIdentifier():
        return False
    if current_token != 'ASGN':
        return False
    else:
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
    print(current_token)
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
    current_token = get_next_token()
    while (declaration()):
        pass
    while (statement() or function()):
        pass
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
    return True

def function():
    global current_token
    if VERBOSE: print("In function.")
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    if not parameter():
        return False
    if current_token != 'RPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'ARROW':
        return False
    current_token = get_next_token()
    if current_token != 'FUNC_KW':
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
    while declaration():
        pass
    while statement():
        pass
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
                    if not comment():
                        if not functionCall():
                            return False
    if current_token != 'ENDSTAT':
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
    while declaration():
        pass
    while statement():
        pass
    if current_token != 'RBRACK':
        return False
    current_token = get_next_token()
    if current_token != 'ELSE_KW':
        return False
    current_token = get_next_token()
    if current_token != 'LBRACK':
        return False
    current_token = get_next_token()
    while declaration():
        pass
    while statement() or function():
        pass
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
    while declaration():
        pass
    while statement():
        pass
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
    if current_token != 'LPAREN':
        return False
    current_token = get_next_token()
    if current_token != 'EQ' and current_token != 'GT':
        return False
    current_token = get_next_token()
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
    return true

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
#    for token in token_gen:
#        print(token)
    if not program():
        print ("Error occured. Read error messages.")
    else:
        print ("Program parsed successfully!")

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        print('No HLPL input file provided for parsing, proceeding with default code.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default, from_parser=True)
    print("Parsing done.")