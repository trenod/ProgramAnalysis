from syntax import *

# Example usage:
# Represents the following WHILE program:
# x := 1;
# WHILE x < 10 DO
#   x := x + 1
# END

# Example from the book, for testing for same results in the book
book_example = CompoundStatement([
    Assignment(Variable('x'), BinaryOperation('+', Variable('a'), Variable('b'))),  # x := a + b;
    Assignment(Variable('y'), BinaryOperation('*', Variable('a'), Variable('b'))),  # y := a * b;
    WhileLoop(
        BinaryOperation('>', Variable('y'), BinaryOperation('+', Variable('a'), Variable('b'))),  # WHILE y > a + b DO
        CompoundStatement([
            Assignment(Variable('a'), BinaryOperation('+', Variable('a'), Constant(1))),  # a := a + 1;
            Assignment(Variable('x'), BinaryOperation('+', Variable('a'), Variable('b')))   # x := a + b
        ])
    )
])


# Program to increment 'x' until it is less than 10
increment_loop = CompoundStatement([
    Assignment(Variable('x'), Constant(0)),  # x := 0;
    WhileLoop(
        BinaryOperation('<', Variable('x'), Constant(10)),  # WHILE x < 10 DO
        CompoundStatement([
            Assignment(Variable('x'), BinaryOperation('+', Variable('x'), Constant(1)))  # x := x + 1
        ])
    )
])


# Program to set 'y' to 1 if 'x' is less than 5, otherwise set 'y' to 0
conditional_assignment = CompoundStatement([
    IfThenElse(
        BinaryOperation('<', Variable('x'), Constant(5)),  # IF x < 5 THEN
        [Assignment(Variable('y'), Constant(1))],  # y := 1
        [Assignment(Variable('y'), Constant(0))]  # ELSE y := 0
    )
])


# Program to increment 'x' and 'y' in nested loops
nested_loops = CompoundStatement([
    Assignment(Variable('x'), Constant(0)),  # x := 0;
    WhileLoop(
        BinaryOperation('<', Variable('x'), Constant(3)),  # WHILE x < 3 DO
        [
            Assignment(Variable('y'), Constant(0)),  # y := 0;
            WhileLoop(
                BinaryOperation('<', Variable('y'), Constant(2)),  # WHILE y < 2 DO
                [
                    Assignment(Variable('y'), BinaryOperation('+', Variable('y'), Constant(1)))  # y := y + 1
                ]
            ),
            Assignment(Variable('x'), BinaryOperation('+', Variable('x'), Constant(1)))  # x := x + 1
        ]
    )
])


# Program that decrements 'x' and if 'x' is odd, increments 'y'
while_with_conditional = CompoundStatement([
    Assignment(Variable('x'), Constant(10)),  # x := 10;
    Assignment(Variable('y'), Constant(0)),  # y := 0;
    WhileLoop(
        BinaryOperation('>', Variable('x'), Constant(0)),  # WHILE x > 0 DO
        [
            Assignment(Variable('x'), BinaryOperation('-', Variable('x'), Constant(1))),  # x := x - 1
            IfThenElse(
                BinaryOperation('%', Variable('x'), Constant(2)),  # IF x % 2 THEN
                [Assignment(Variable('y'), BinaryOperation('+', Variable('y'), Constant(1)))],  # y := y + 1
                []
            )
        ]
    )
])
