#this program contains different classes to create the nodes of our parse tree
#each class contains a constructor and a display method that will be used later
#to display our cst starting from the root

#this program is imported in parse.py


class TypeNode:
    def __init__(self, value: str):
        self.value = value  # num or ascii for now
    def display(self):
        print('--typespec--')
        print(self.value)

class UserDefinedNode:
    def __init__(self, name: str):
        self.name = name
    def display(self):
        print('--userdefined--')
        print(self.name)

class VarDeclarationNode:
    def __init__(self, typespec: TypeNode, identifier: UserDefinedNode):
        self.typespec = typespec
        self.identifier = identifier
    def display(self):
        print('--var.datatype--')
        self.typespec.display()
        print('--var.ident--')
        self.identifier.display()

class NumLiteralNode:
    def __init__(self, value: int):
        self.value = value
    def display(self):
        print('--numlit.value--')
        print(self.value)

class OperandNode:
    def __init__(self, num: NumLiteralNode, uid: UserDefinedNode, \
        op, call):  # sadly, I have to remove type hints here because i can't keep shifting interdependent class definitions
        if num:
            self.type = 'numlit'
            self.value = num
        elif uid:
            self.type = 'userdefined'
            self.value = uid
        elif op:
            self.type = 'operation'
            self.value = op
        elif call:
            self.type = 'funcall'
            self.value = call
        else:
            raise Exception('no match on operand node')
    def display(self):
        print('--operand.type--')
        print(self.type)
        print(f'--operand.{self.type}--')
        self.value.display()


class AddNode():
    def __init__(self, opd1: OperandNode, opd2: OperandNode):
        self.opd1 = opd1
        self.opd2 = opd2
    def display(self):
        print('--add node--')
        print('--opd1--')
        self.opd1.display()
        print('--opd2--')
        self.opd2.display()

class SubNode:
    def __init__(self, opd1: OperandNode, opd2: OperandNode):
        self.opd1 = opd1
        self.opd2 = opd2
    def display(self):
        print('--sub node--')
        print('--opd1--')
        self.opd1.display()
        print('--opd2--')
        self.opd2.display()

class MultNode:
    def __init__(self, opd1: OperandNode, opd2: OperandNode):
        self.opd1 = opd1
        self.opd2 = opd2
    def display(self):
        print('--mult node--')
        print('--opd1--')
        self.opd1.display()
        print('--opd2--')
        self.opd2.display()

class DivNode:
    def __init__(self, opd1: OperandNode, opd2: OperandNode):
        self.opd1 = opd1
        self.opd2 = opd2
    def display(self):
        print('--div node--')
        print('--opd1--')
        self.opd1.display()
        print('--opd2--')
        self.opd2.display()

class OperationNode:
    def __init__(self, op: int, opd1: OperandNode, opd2: OperandNode):
        if op == 1:
            self.type = 'add'
            self.value = AddNode(opd1, opd2)
        elif op == 2:
            self.type = 'sub'
            self.value = SubNode(opd1, opd2)
        elif op == 3:
            self.type = 'mult'
            self.value = MultNode(opd1, opd2)
        elif op == 4:
            self.type = 'div'
            self.value = DivNode(opd1, opd2)
        else:
            raise Exception('no match in operation node')
    def display(self):
        print('--operation.type--')
        print(self.type)
        print(f'--operation.{self.type}--')
        self.value.display()
        
class ReservedNode:
    def __init__(self, value: str):
        self.value = value  # write or read
    def display(self):
        print('--reserved--')
        print(self.value)

class IdentifierNode:
    def __init__(self, udi: UserDefinedNode, res: ReservedNode):
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
        self.name = name
        self.args = args  # list[ExpressionNode]
    def display(self):
        print('--funcall.name--')
        self.name.display()
        print('--funcall.args--')
        [arg.display() for arg in self.args]

class StringLiteralNode:
    def __init__(self, value: str):
        self.value = value
    def display(self):
        print('--strlit.value--')
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
        num: NumLiteralNode, udi: UserDefinedNode, op: OperationNode):
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
        elif op:
            self.type = 'op'
            self.value = op
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
        if var:
            self.type = 'var'
            self.value = var
        elif fix:
            self.type = 'fix'
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
        self.name = name
        self.args = args
        self.return_type = return_type
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
        print(f'--assign.{self.type}--')
        self.value.display()

class ParamNode:
    def __init__(self, type: TypeNode, name: UserDefinedNode):
        self.typespec = type
        self.name = name
    def display(self):
        print('--param.datatype--')
        self.typespec.display()
        print('--param.name--')
        self.name.display()

class ReturnNode:
    def __init__(self, exp: ExpressionNode, call: CallNode):
        if exp:
            self.type = 'expression'
            self.value = exp
        elif call:
            self.type = 'funcall'
            self.value = call
        else:
            raise Exception('nothing matches on return node')
    def display(self):
        print('--return.type--')
        print(self.type)
        print(f'--return.{self.type}--')
        self.value.display()

class ComparedNode:
    def __init__(self, n_node: NumLiteralNode, u_node: UserDefinedNode, f_node: CallNode):
        if n_node:
            self.type = 'numlit'
            self.value = n_node
        elif u_node:
            self.type = 'userdefined'
            self.value = u_node
        elif f_node:
            self.type = 'funcall'
            self.value = f_node
        else:
            raise Exception('nothing matches on compared node')
    def display(self):
        print('--compared.type--')
        print(self.type)
        print('--compared.value--')
        self.value.display()

class ComparisonNode:
    def __init__(self, operator: str, comp1: ComparedNode, comp2: ComparedNode):
        self.type = operator.lower()
        self.comp1 = comp1
        self.comp2 = comp2
    def display(self):
        print('--comparison.type--')
        print(self.type)
        print('--compared1--')
        self.comp1.display()
        print('--compared2--')
        self.comp2.display()

class ConditionNode:
    def __init__(self, comparison: ComparisonNode):
        # let's ignore boolean operators for now
        # two possible conditions: eq or gt
        self.value = comparison
    def display(self):
        print('--condition--')
        self.value.display()

class SelectionNode:
    def __init__(self, condition, then: list, _else: list):
        # all our selections are 2-way
        # condition (combination of EQs or GTs with AND, OR, or NOT), 
        # then (List[StatementNode]),
        # else (same as then)
        # because we're not doing blocks
        self.condition = condition
        self.then = then
        self._else = _else  # i mean, it's fine to just write else, but that's pretty confusing
    def display(self):
        print('--selection.condition--')
        self.condition.display()
        print('--selection.then--')
        [stat.display() for stat in self.then]
        print('--selection.else--')
        [stat.display() for stat in self._else]

class LoopNode:
    def __init__(self, condition: ConditionNode, stats: list):
        # condition, list of statements
        self.condition = condition
        self.body = stats
    def display(self):
        print('--loop.condition--')
        self.condition.display()
        print('--loop.body--')
        [stat.display() for stat in self.body]

class StatementNode:
    def __init__(self, a_node: AssignmentNode, r_node: ReturnNode, s_node: SelectionNode,\
            l_node: LoopNode, f_node: CallNode):
        if a_node:
            self.type = 'assign'
            self.value = a_node
        elif r_node:
            self.type = 'give'
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
        print(f'--stat.{self.type}--')
        self.value.display()            

class MainNode:
    def __init__(self, declarations: list, statements: list):
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
        self.declarations = declarations
        self.functions = functions
        self.main = main_node
    def display(self):
        print('--prog.decs--')
        [dec.display() for dec in self.declarations]
        print('--prog.funcs--')
        [func.display() for func in self.functions]
        print('--prog.main--')
        self.main.display()
