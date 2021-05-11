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
        # one of them will be Falsy (False or None, haven't decided yet, but doesn't matter)
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
