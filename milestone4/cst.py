class TypeNode:
    def __init__(self, value: str):
        print('init type')
        self.value = value  # num or ascii for now
    def display(self):
        print('--typespec--')
        print(self.value)

class UserDefinedNode:
    def __init__(self, name: str):
        print('init userdefine')
        self.name = name
    def display(self):
        print('--userdefined--')
        print(self.name)

class VarDeclarationNode:
    def __init__(self, typespec: TypeNode, identifier: UserDefinedNode):
        print('init var')
        self.typespec = typespec
        self.identifier = identifier
    def display(self):
        print('--var.datatype--')
        self.typespec.display()
        print('--var.ident--')
        self.identifier.display()

class OperationNode:
    def __init__(self):
        print('init op')

class ReservedNode:
    def __init__(self, value: str):
        print('init reserved')
        self.value = value  # write or read
    def display(self):
        print('--reserved--')
        print(self.value)

class IdentifierNode:
    def __init__(self, udi: UserDefinedNode, res: ReservedNode):
        print('init id')
        if udi:
            self.type = 'userdefined'
            self.value = udi
        elif res:
            self.type = 'reserved'
            self.value = res
        else:
            raise Exception("nothing matches in id node")
    def display(self):
        print('--ident.type--')
        print(self.type)
        print(f'--ident.{self.type}--')
        self.value.display()

class CallNode:  # function call
    def __init__(self, name: IdentifierNode, args: list):
        print('init call')
        self.name = name
        self.args = args  # list[ExpressionNode]
    def display(self):
        print('--funcall.name--')
        self.name.display()
        print('--funcall.args--')
        [arg.display() for arg in self.args]

class StringLiteralNode:
    def __init__(self, value: str):
        print('init str')
        self.value = value
    def display(self):
        print('--strlit.value--')
        print(self.value)

class NumLiteralNode:
    def __init__(self, value: int):
        print('init numlit')
        self.value = value
    def display(self):
        print('--numlit.value--')
        print(self.value)

class CharLiteralNode:
    def __init__(self, value: str):
        print('init charlit')
        self.value = value
    def display(self):
        print('--charlit.value--')
        print(self.value)

class ExpressionNode:
    def __init__(self, char: CharLiteralNode, string: StringLiteralNode, \
        num: NumLiteralNode, udi: UserDefinedNode):
        print('init expr')
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
    def display(self):
        print('--expr.type--')
        print(self.type)
        print(f'--expr.{self.type}--')
        self.value.display()
        
class FixDeclarationNode:
    def __init__(self, typespec: TypeNode, identifier: UserDefinedNode, exp: ExpressionNode, \
        op: OperationNode, call: CallNode):
        print('init fix')
        self.typespec = typespec
        self.identifier = identifier
        if exp:
            self.type = 'expression'
            self.value = exp
        elif op:
            self.type = 'operation'
            self.value = op
        elif call:
            self.type = 'call'
            self.value = call
        else:
            raise Exception("nothing matches in fix dec node")
    def display(self):
        print('--fix.type--')
        print(self.type)
        print('--fix.ident--')
        self.identifier.display()
        print(f'--fix.{self.type}--')
        self.value.display()

class DeclarationNode:
    def __init__(self, var: VarDeclarationNode, fix: FixDeclarationNode):
        print('init dec')
        if var:
            self.type = 'variable'
            self.value = var
        elif fix:
            self.type = 'constant'
            self.value = fix
        else:
            raise Exception("nothing matches in declaration node")
    def display(self):
        print('--dec.type--')
        print(self.type)
        print(f'--dec.{self.type}--')
        self.value.display()

class FunctionNode:
    def __init__(self, name: UserDefinedNode, args: list, return_type: TypeNode, \
         declarations: list, statements: list):
        print('init func')
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

class AssignmentNode:
    def __init__(self, identifier: UserDefinedNode, exp: ExpressionNode, \
        op: OperationNode, call: CallNode):
        print('init assign')
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
    def display(self):
        print('--assign.type--')
        print(self.type)
        print('f--assign.{self.type}--')
        self.value.display()

class ParamNode:
    def __init__(self, type: TypeNode, name: UserDefinedNode):
        print('init param')
        self.type = type
        self.name = name
    ##

class ReturnNode:
    def __init__(self, exp: ExpressionNode, call: CallNode):
        print('init return')
        if exp:
            self.type = 'expression'
            self.value = exp
        elif call:
            self.type = 'funcall'
            self.value = call
        else:
            raise Exception('nothing matches on return node')
    ##

class SelectionNode:
    def __init__(self):
        pass

class LoopNode:
    def __init__(self):
        pass

class StatementNode:
    def __init__(self, a_node: AssignmentNode, r_node: ReturnNode, s_node: SelectionNode,\
            l_node: LoopNode, f_node: CallNode):
        print('init stat')
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

class MainNode:
    def __init__(self, declarations: list, statements: list):
        print('init main')
        # we won't implement nested functions
        self.declarations = declarations  # of type DeclarationNode
        self.statements = statements  # of type StatementNode
    def display(self):
        print('--main.decs--')
        [dec.display() for dec in self.declarations]
        print('--main.stats--')
        [stat.display() for stat in self.statements]
    
class ProgramNode:
    def __init__(self, declarations: list, functions: list, main_node: MainNode):
        print('init prog')
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
        