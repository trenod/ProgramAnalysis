# Expression types
from typing import List


class Expression:
    pass


class Variable(Expression):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Variable({self.name})"


class Constant(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Constant({self.value})"


class BinaryOperation(Expression):
    def __init__(self, op: str, left: Expression, right: Expression):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryOperation({self.op}, {self.left}, {self.right})"


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


class Assignment(Statement):
    def __init__(self, variable: Variable, expression: Expression):
        self.variable = variable
        self.expression = expression

    def __repr__(self):
        return f"Assignment({self.variable}, {self.expression})"


class WhileLoop(Statement):
    def __init__(self, condition: Expression, body: CompoundStatement):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileLoop({self.condition}, {self.body})"


class IfThenElse(Statement):
    def __init__(self, condition: Expression, true_branch: CompoundStatement, false_branch: CompoundStatement):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __repr__(self):
        return f"IfThenElse({self.condition}, {self.true_branch}, {self.false_branch})"
