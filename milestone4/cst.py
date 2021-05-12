from os import stat


class ParseTreeNode():
    # If any functions are general to all tree nodes,
    # they should be put here
    # maybe a display() function will come in handy
    # but we'll need one for each subclass as well
    # if there are no shared functions aamong these, no need for inheritance
    pass

class TypeNode(ParseTreeNode):
    def __init__(self, value: str):
        self.value = value  # num, ascii

class VarDeclarationNode(ParseTreeNode):
    def __init__(self, typespec: TypeNode, identifier: str):
        self.typespec = typespec
        self.identifier = identifier

class OperationNode():
    def __init__(self):
        pass

class UserDefinedNode(ParseTreeNode):
    def __init__(self, name: str):
        self.name = name

class ReservedNode(ParseTreeNode):
    def __init__(self, value: str):
        self.value = value  # write or read

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

class CallNode(ParseTreeNode):  # function call
    def __init__(self, name: IdentifierNode, args: list):
        self.name = name
        self.args = args  # list[ExpressionNode]

class StringLiteralNode(ParseTreeNode):
    def __init__(self, value: str):
        self.value = value

class NumLiteralNode(ParseTreeNode):
    def __init__(self, value: int):
        self.value = value

class CharLiteralNode(ParseTreeNode):
    def __init__(self, value: str):
        self.value = value

class ExpressionNode(ParseTreeNode):
    def __init__(self, char: CharLiteralNode, string: StringLiteralNode, \
        udi: UserDefinedNode, num: NumLiteralNode):
        if char:
            self.type = 'char'
            self.value = char
        elif string:
            self.type = 'str'
            self.value = string
        elif num:
            self.type = 'num'
            self.value = num
        elif udi:
            self.type = 'userdefined'
            self.value = udi
        else:
            raise Exception('nothing matches on expr node')
        
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
    def __init__(self, name: UserDefinedNode, args: list, return_type: TypeNode, \
         declarations: list, statements: list):
        self.name = name
        self.args = args
        self.return_type = return_type  # can be None
        self.declarations = declarations
        self.statements = statements

    def display(self):
        print('--func.name--')
        self.name.display()
        print('--func.args--')
        [arg.display() for arg in self.args]
        print('--func.return_type--')
        if self.return_type:
            self.return_type.display()
        else:
            print('None')
        print('--func.decs--')
        [dec.display() for dec in self.declarations]
        print('--func.stats--')
        [stat.display() for stat in self.statements]

class AssignmentNode(ParseTreeNode):
    def __init__(self, identifier: UserDefinedNode, exp: ExpressionNode, \
        op: OperationNode, call: CallNode):
        self.identifier = identifier
        if exp:
            self.type = 'expression'
            self.value = exp
        elif op:
            self.type = 'operation'
            self.value = op
        elif call:
            self.type = 'funcall'
            self.value = call
        else:
            raise Exception("no match on assign node")

class ParamNode(ParseTreeNode):
    def __init__(self, type: TypeNode, name: UserDefinedNode):
        self.type = type
        self.name = name

class ReturnNode(ParseTreeNode):
    def __init__(self, exp: ExpressionNode, call: CallNode):
        if exp:
            self.type = 'expression'
            self.value = exp
        elif call:
            self.type = 'funcall'
            self.value = call
        else:
            raise Exception('nothing matches on return node')

class SelectionNode(ParseTreeNode):
    def __init__(self):
        pass

class LoopNode(ParseTreeNode):
    def __init__(self):
        pass

class StatementNode(ParseTreeNode):
    def __init__(self, a_node: AssignmentNode, r_node: ReturnNode, s_node: SelectionNode,\
         l_node: LoopNode, f_node: CallNode):
        if a_node:
            self.type = 'assign'
            self.value = a_node
        elif r_node:
            self.type = 'return'
            self.value = r_node
        elif s_node:
            self.type = 'selection'
            self.value = s_node
        elif l_node:
            self.type = 'loop'
            self.value = l_node
        elif f_node:
            self.type = 'funcall'
            self.value = f_node
        else:
            raise Exception("nothing matches on statement node")
    
    def display(self):
        print('--stat.type--')
        print(self.type)
        print(f'--stat.{self.type}')
        self.value.display()            

class MainNode(ParseTreeNode):  # this means inheritance
    def __init__(self, declarations: list, statements: list):
        # we won't implement nested functions
        self.declarations = declarations  # of type DeclarationNode
        self.statements = statements  # of type StatementNode

    def display(self):
        print('--main.decs--')
        [dec.display() for dec in self.declarations]
        print('--main.stats--')
        [stat.display() for stat in self.statements]
    
class ProgramNode(ParseTreeNode):
    def __init__(self, declarations: list, functions: list, main_node: MainNode):
        if not main_node:
            raise Exception("Input program lacks entry function.")
        self.declarations = declarations
        self.functions = functions
        self.main_node = main_node
    
    def display(self):
        print('--prog.main--')
        self.main_node.display()
        print('--prog.decs--')
        [dec.display() for dec in self.declarations]
        print('--prog.funcs--')
        [func.display() for func in self.functions]
        