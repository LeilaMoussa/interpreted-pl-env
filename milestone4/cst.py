class ParseTreeNode():
    # If any functions are general to all tree nodes,
    # they should be put here
    # maybe a display() function will come in handy
    # but we'll need one for each subclass as well
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
    def __init__(self, typespec: TypeNode, identifier: UserDefinedNode, exp: ExpressionNode, \
        op: OperationNode, call: CallNode):
        self.typespec = typespec
        self.identifier = identifier
        if exp:
            self.type = 'expression'  # debating whether this is okay
            self.value = exp
        elif op:
            self.type = 'operation'
            self.value = op
        elif call:
            self.type = 'call'
            self.value = call
        else:
            raise Exception("nothing matches in fix dec node")

class DeclarationNode(ParseTreeNode):
    def __init__(self, var: VarDeclarationNode, fix: FixDeclarationNode):
        # one of them will be Falsy (False or None, haven't decided yet, but doesn't matter)
        if var:
            self.type = 'variable'
            self.value = var
        elif fix:
            self.type = 'constant'
            self.value = var
        else:
            raise Exception("nothing matches in declaration node")  # shouldn't happen ofc

class FunctionNode(ParseTreeNode):
    def __init__(self, name: UserDefinedNode, arg: list, return_type: TypeNode, \
         declarations: list, statements: list):
        # args is most likely a list of parameter objects
        # args may be empty
        # return_type may be None
        # decs & statements are lists of their respective nodes, potentially empty
        pass

class TypeNode(ParseTreeNode):
    def __init__(self, value: str):
        self.value = value  # num, ascii

class StatementNode(ParseTreeNode):
    def __init__(self):
        # indicate the type of the statement and its associated info
        pass

class CallNode(ParseTreeNode):  # function call
    def __init__(self, name: IdentifierNode, args: list):
        self.name = name
        self.args = args  # list[ExpressionNode]

class AssignmentNode(ParseTreeNode):
    def __init__(self, identifier: IdentifierNode): # and a bunch of possibilities
        self.identifier = identifier

class IdentifierNode(ParseTreeNode):
    def __init__(self, udi: UserDefinedNode, res: ReservedNode):
        if udi:
            self.type = 'userdefined'
            self.value = udi
        elif res:
            self.type = 'reserved'
            self.value = res
        else:
            raise Exception("nothing matches in id node")

class UserDefinedNode(ParseTreeNode):
    def __init__(self, name: str):
        self.name = name

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

class CharLiteralNode(ParseTreeNode):
    def __init__(self, value: str):
        self.value = value

class ExpressionNode(ParseTreeNode):
    def __init__(self, type, value):  # uhmm
        pass

class ParamNode(ParseTreeNode):
    def __init__(self, type: TypeNode, name: UserDefinedNode):
        self.type = type
        self.name = name

# etc.