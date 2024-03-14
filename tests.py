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

        # Creating the CFG also creates the nodes
        self.cfg = (self.analysis.mkDFS(root, set()))
        self.nodes = self.analysis.nodes

    def test_create_cfg(self):
        self.previous_node = self.cfg[0]
        for node in self.cfg:
            # Check if the node is a tuple
            assert isinstance(node, tuple)
            print("{node}, ")
            (fst, snd) = node
            assert isinstance(fst, int)
            if snd != 'exit':
                assert isinstance(snd, int) 

    def test_nodes(self):
        self.assertEqual(len(self.cfg), len(self.nodes))
        for node in self.nodes.values():
            print(f"Node with label {node.label} has the following information: \n")
            # Either a statement or an expression (or None if it's an exit node)
            print(f"Statement: {node.stmt}\n")
            print(f"Expression: {node.expression}\n")
            print(f"Is exit: {node.is_exit()}\n")
            # Predecessors and successors
            #print(f"Coming in: {node.coming_in}\n")
            #print(f"Going out: {node.going_out}\n")
            # Gen, kill, entry, and exit sets
            print(f"Generated expressions: {node.gen}\n")
            print(f"Killed expressions: {node.kill}\n")
            print(f"Entry: {node.entry}\n")
            print(f"Exit: {node.exit}\n")

    def test_book_example(self):
        # Test book example for correct cfg and nodes
        self.assertEqual(self.cfg, [(1, 2), (2, 3), (3, 4), (4,5), (5, 3), (3, 'exit')])
        # Test that the nodes are correctly labeled
        for i in range(1, (len(self.nodes))):
            if (i == (len(self.nodes))):
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
