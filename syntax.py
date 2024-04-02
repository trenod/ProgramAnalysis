# Expression types
from typing import List


class Expression:
    pass


class Variable(Expression):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Variable({self.name})"
    
    def __hash__(self):
        return hash((self.name, 'Variable'))

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name


class Constant(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Constant({self.value})"
    
    def __hash__(self):
        return hash((self.value, 'Constant'))

    def __eq__(self, other):
        return isinstance(other, Constant) and self.value == other.value


class BinaryOperation(Expression):
    def __init__(self, op: str, left: Expression, right: Expression):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryOperation({self.op}, {self.left}, {self.right})"
    
    def __hash__(self):
        return hash((self.op, self.left, self.right, 'BinaryOperation'))

    def __eq__(self, other):
        return (isinstance(other, BinaryOperation) and self.op == other.op and 
                self.left == other.left and self.right == other.right)


# Statement types
class Statement:
    pass


class CompoundStatement(Statement):
    def __init__(self, statements: List[Statement]):
        self.statements = statements

    '''
    def __iter__(self):
        current = self.head
        while current is not None:
            yield current
            current = current.next
    '''
    def __iter__(self):
        return iter(self.statements)


    def __repr__(self):
        return f"CompoundStatement({self.statements})"
    
    def __hash__(self):
        return hash(tuple(self.statements))

    def __eq__(self, other):
        return isinstance(other, CompoundStatement) and self.statements == other.statements


class Assignment(Statement):
    def __init__(self, variable: Variable, expression: Expression):
        self.variable = variable
        self.expression = expression

    def __repr__(self):
        return f"Assignment({self.variable}, {self.expression})"
    
    def __hash__(self):
        return hash((self.variable, self.expression))

    def __eq__(self, other):
        return isinstance(other, Assignment) and self.variable == other.variable and self.expression == other.expression


class WhileLoop(Statement):
    def __init__(self, condition: Expression, body: CompoundStatement):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileLoop({self.condition}, {self.body})"
    
    def __hash__(self):
        return hash((self.condition, self.body))

    def __eq__(self, other):
        return isinstance(other, WhileLoop) and self.condition == other.condition and self.body == other.body


class IfThenElse(Statement):
    def __init__(self, condition: Expression, true_branch: CompoundStatement, false_branch: CompoundStatement):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __repr__(self):
        return f"IfThenElse({self.condition}, {self.true_branch}, {self.false_branch})"

    def __hash__(self):
        return hash((self.condition, self.true_branch, self.false_branch))

    def __eq__(self, other):
        return (isinstance(other, IfThenElse) and self.condition == other.condition and
                self.true_branch == other.true_branch and self.false_branch == other.false_branch)

class Skip(Statement):
    def __repr__(self):
        return "Skip"