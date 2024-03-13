import unittest

from AvailableExpressions import *
from examples import *


class TestAvailableExpressionsAnalysis(unittest.TestCase):

    def setUp(self):
        # Code here will run before each test method
        self.analysis = AvailableExpressionsAnalysis()

        (root, exits) = self.analysis.create_cfg_statement(book_example)
    
        # Need a final patch-up!
        the_exit = Node()
        the_exit.label = "exit"
        the_exit.going_out = []
        for e in exits:
            e.going_out.append(the_exit)
        the_exit.is_exit = True

        self.cfg = (self.analysis.mkDFS(root, set()))
        self.nodes = self.analysis.nodes
        self.analysis.nodes[len(self.nodes) + 1] = the_exit

    def test_create_cfg(self):
        self.previous_node = self.cfg[0]
        for node in self.cfg:
            # Check if the node is a tuple
            assert isinstance(node, tuple)
            print("{node}, ")
            # Check if successors have a higher label than predecessors
            # i.e (1, 2) < (2, 3)
            (fst, snd) = node
            (fstprev, sndprev) = self.previous_node
            #self.assertLessEqual(fstprev, fst)
            #self.assertLessEqual(sndprev, snd)
            self.previous_node = node
            

    def test_nodes(self):
        self.assertEqual(len(self.cfg) +1, len(self.nodes))
        for node in self.nodes.values():
            print(f"Node with label {node.label} has the following information: \n")
            print(f"Statement: {node.stmt}\n")
            print(f"Expression: {node.expression}\n")
            print(f"Coming in: {node.coming_in}\n")
            print(f"Going out: {node.going_out}\n")
            print(f"Generated expressions: {node.gen}\n")
            print(f"Killed expressions: {node.kill}\n")

    def test_book_example(self):
        # Test book example for correct cfg and nodes
        self.assertEqual(self.cfg, [(1, 2), (2, 3), (3, 4), (4,5), (5, 3), (3, 'exit')])
        # Test that the nodes are correct
        for i in range(1, 6):
            if (i == 6):
                self.assertEqual(self.nodes[i].label, 'exit')
                break
            self.assertEqual(self.nodes[i].label, i)

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
        if isinstance(stmt, Skip):
            pass
        elif isinstance(stmt, Assignment):
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
