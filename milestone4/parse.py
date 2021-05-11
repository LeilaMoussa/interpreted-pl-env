import sys
import os
sys.path.append(os.path.abspath('../milestone3'))
from lex import main as generate

# good idea: put classes in a file called AST.py

VERBOSE = True

token_gen = None  # token_gen is a generator object of (token, lexeme, line_number)
current_token = None
line = -1
position = -1

class ParseTreeNode():
    # If any functions are general to all tree nodes,
    # they should be put here
    pass

class ProgramNode(ParseTreeNode):
    def __init__(self, declarations: list, functions: list, mainFunction: MainNode):
        self.declarations = declarations
        self.functions = functions
        self.mainFunction = mainFunction

    def append_declaration(self, dec: DeclarationNode):
        self.declarations.append(dec)

    def append_function(self, func: FunctionNode):
        self.functions.append(func)

class MainNode(ParseTreeNode):  # this means inheritance
    def __init__(self, declarations: list, statements: list):
        # we won't implement nested functions
        self.declarations = declarations  # of type DeclarationNode
        self.statements = statements  # of type StatementNode

    def append_declaration(self, dec: DeclarationNode):
        self.declarations.append(dec)

    def append_statement(self, stat: StatementNode):
        self.statements.append(stat)

class VarDeclarationNode(ParseTreeNode):
    def __init__(self, typespec: TypeNode, identifier: str):
        self.typespec = typespec
        self.identifier = identifier

class FixDeclarationNode(ParseTreeNode):
    def __init__(self, typespec: TypeNode, identifier: str, value):
        self.typespec = typespec
        self.identifier = identifier
        self.value = value  # could be a number or a character at this point
        # since we don't have strings or arrays implemented yet

class DeclarationNode(ParseTreeNode):
    def __init__(self, var: VarDeclarationNode, fix: FixDeclarationNode):
        if var:
            self.type = 'variable'
            self.info = var
        elif fix:
            self.type = 'constant'
            self.info = var
        else:
            raise Exception("nothing matches in declaration node")  # shouldn't happen ofc

class FunctionNode(ParseTreeNode):
    def __init__(self, name: IdentifierNode, arguments: list, return_type: TypeNode, \
         declarations: list, statements: list):
        pass

class TypeNode(ParseTreeNode):
    def __init__(self, value: str):
        self.value = value  # num, ascii

class StatementNode(ParseTreeNode):
    def __init__(self):
        # indicate the type of the statement and its associated info
        pass

class CallNode(ParseTreeNode):  # function call
    def __init__(self, name, )

class AssignmentNode(ParseTreeNode):
    def __init__(self, identifier: IdentifierNode, rhs):
        self.identifier = identifier
        # rhs could be ExpressionNode, OperationNode, or CallNode
        # based on its type, set self.type
        # or should be do this the same way as DeclarationNode? i.e. supply all
        # possible types and one of them is not null

class IdentifierNode(ParseTreeNode):
    pass

class ReservedNode(ParseTreeNode):
    def __init__(self, value: str):
        self.value = value  # write or read

# i think these will be needed for static semantics
class StringLiteralNode(ParseTreeNode):
    def __init__(self, value: str):
        self.value = value

class NumLiteralNode(ParseTreeNode):
    def __init__(self, value: int):
        self.value = value
        # i wonder if we'll need a sign property (positive, negative) for the AL

# etc.

def get_next_token():
    global token_gen, line, position
    try:
        token_info = token_gen.__next__()
        line += 1
        position += 1
        token = token_info[0]
        if VERBOSE: print("Current token:", token)
        return token
    except:
        sys.exit("Reached end of token stream with no errors!")

def program():
    global current_token
    if VERBOSE: print("In program.")
    local_position = position
    while declaration():
        local_position = position
    if position > local_position: return False  # by virtue of LL(1)
    while function():
        local_position = position
    if position > local_position: return False
    if not mainFunction():
        return False
    return True
        
def declaration():
    global current_token
    # local_node = DeclarationNode()
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
