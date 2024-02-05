import unittest

from AvailableExpressions import *
from examples import *


class TestAvailableExpressionsAnalysis(unittest.TestCase):

    def setUp(self):
        # Code here will run before each test method
        analysis = AvailableExpressionsAnalysis()
        self.cfg = analysis.create_cfg(increment_loop)
        self.nodes = analysis.nodes

    def test_create_cfg(self):
        self.previous_node = self.cfg[0]
        for node in self.cfg:
            # Check if the node is a tuple
            isinstance(node, tuple)
            print("{node}, ")
            # Check if successors have a higher label than predecessors
            # i.e (1, 2) < (2, 3)
            (fst, snd) = node
            (fstprev, sndprev) = self.previous_node
            self.assertLessEqual(fstprev, fst)
            self.assertLessEqual(sndprev, snd)
            self.previous_node = node
            

    def test_nodes(self):
        self.assertEqual(len(self.cfg), len(self.nodes))
        for node in self.nodes:
            print("Node with label {node.label} has the following information: \n")
            print("Statement: {node.stmt}\n")
            print("Expression: {node.expression}\n")
            print("Predecessors: {node.predecessors}\n")
            print("Successors: {node.successors}\n")
            print("Generated expressions: {node.gen}\n")
            print("Killed expressions: {node.kill}\n")

    def test_analysis(self):
        pass


class TestDynamicProgramStructure(unittest.TestCase):

    def check_expression(self, expr):
        if isinstance(expr, Variable):
            self.assertIsInstance(expr.name, str)
        elif isinstance(expr, Constant):
            self.assertIsInstance(expr.value, int)
        elif isinstance(expr, BinaryOperation):
            self.assertIsInstance(expr.op, str)
            self.check_expression(expr.left)
            self.check_expression(expr.right)
        else:
            self.fail(f"Unknown Expression type: {type(expr)}")

    def check_statement(self, stmt):
        if isinstance(stmt, Assignment):
            self.assertIsInstance(stmt.variable, Variable)
            self.check_expression(stmt.variable)
            self.check_expression(stmt.expression)
        elif isinstance(stmt, WhileLoop):
            self.check_expression(stmt.condition)
            for s in stmt.body:
                self.check_statement(s)
        elif isinstance(stmt, IfThenElse):
            self.check_expression(stmt.condition)
            for s in stmt.true_branch:
                self.check_statement(s)
            for s in stmt.false_branch:
                self.check_statement(s)
        elif isinstance(stmt, CompoundStatement):
            for s in stmt.statements:
                self.check_statement(s)
        else:
            self.fail(f"Unknown Statement type: {type(stmt)}")

    def test_arbitrary_program_structure(self):
        programs = [increment_loop, conditional_assignment, nested_loops, while_with_conditional]
        for prog in programs:
            self.assertIsInstance(prog, CompoundStatement)
            for stmt in prog.statements:
                self.check_statement(stmt)


if __name__ == '__main__':
    unittest.main()
