from typing import List, Union, Callable

# Expression types
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


# Example usage:
# Represents the following WHILE program:
# x := 1;
# WHILE x < 10 DO
#   x := x + 1
# END

# Program to increment 'x' until it is less than 10
increment_loop = CompoundStatement([
    Assignment(Variable('x'), Constant(0)),  # x := 0;
    WhileLoop(
        BinaryOperation('<', Variable('x'), Constant(10)),  # WHILE x < 10 DO
        [
            Assignment(Variable('x'), BinaryOperation('+', Variable('x'), Constant(1)))  # x := x + 1
        ]
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


import unittest

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


class Node:
    def __init__(self):
        self.label = None   # Label for this node in the control flow graph
        self.stmt = None    # Statement represented by this node
        self.gen = set()    # Expressions generated in this node
        self.kill = set()   # Expressions killed in this node
        self.entry = set()  # Assignments live at entry to this node
        self.exit = set()   # Assignments live at exit from this node
        self.predecessors = list() # Predecessor nodes in the control flow graph
        self.successors = list() # Successor nodes in the control flow graph
        self.entry_state = None  # Analysis state at entry to this node (used for chaotic iteration)
        self.exit_state = None  # Analysis state at exit from this node (used for chaotic iteration)

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current
            current = current.next

    def __repr__(self):
        return f"Node(use={self.use}, entry={self.entry}, exit={self.exit})"
    
    def add_successor(self, node):
        self.successors.append(node)
        node.predecessors.append(self)


from abc import ABC, abstractmethod
from typing import Set

class DataFlowAnalysis(ABC):
    def __init__(self, initial_state):
        self.initial_state = initial_state
        self.killed = list()
        self.generated = list()
        self.list_of_nodes = list()
        self.label = 0
        self.cfg = list((int, int))

    def initial_node(self):
        for node in self.list_of_nodes:
            if node.label == 1:
                #only need entry state for initial node?
                node.entry = self.initial_state
                #node.exit = self.initial_state
                return node
    
    def final_node(self):
        final_node = Node()
        final_node.label = 1
        for node in self.list_of_nodes:
            if node.label > final_node.label:
                final_node = node
        return final_node

    @abstractmethod
    def flow(self):
        pass


    @abstractmethod
    def create_cfg(self):
        for node in self.list_of_nodes:
            for successor in node.successors:
                self.cfg.append((node.label, successor.label))

    @abstractmethod
    def transfer_function(self, node, state):
        """
        The transfer function applies the analysis-specific rules to update the state for a given node.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def merge(self, states):
        """
        The merge function defines how to combine states from different predecessors.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def compare(self, state1, state2):
        """
        The compare function checks whether two analysis states are equal.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def gen_function(self, expr: Expression) -> Set[str]:
        """
        The gen function defines which variables are generated by an expression.
        By default, no variables are generated.
        """
        return set()
    
    @abstractmethod
    def kill_function(self, expr: Expression) -> Set[str]:
        """
        The kill function defines which variables are killed by an expression.
        By default, no variables are killed.
        """
        return set()
    
    @abstractmethod
    def create_nodes(self, stmt: Statement) -> Node:
        """
        The create_nodes function creates a list of nodes from a statement.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def analyze(self, nodes):
        """
        The analyze function applies the chaotic iteration algorithm to reach a fixpoint.
        """

    @abstractmethod
    def print_nodes(self, node, nodes, visited=None, level=0):
        if (nodes is None) or (len(nodes) == 0):
            return
        
        if node is not None:
            currentnode = node
        else: 
            currentnode = nodes[0]
            
        nodes.remove(currentnode)
            
        if visited is None:
            visited = set()

        # Add the current node to the visited set
        visited.add(currentnode)

        indent = "  " * level
        print(f"{indent}Node - Entry: {currentnode.entry}, Exit: {currentnode.exit}")

        # Iterate over successors
        for succ in currentnode.successors:
            if succ not in visited:
                self.print_nodes(succ, nodes, visited, level+1)
        


# Reaching definitions analysis     
class ReachingDefinitions(DataFlowAnalysis):
    def __init__(self, initial_state):
        super().__init__(initial_state)

    def initial_node(self):
        return super().initial_node()

    def final_node(self):
        return super().final_node()
    
    def flow(self):
        return super().flow()

    def create_cfg(self):
        return super().create_cfg(self)

    def transfer_function(self, node, state):
        #should I have calls to kill and gen functions here?
        if isinstance(node.stmt, Assignment):
            # Remove any previous definitions of the same variable
            var_name = node.stmt.lhs.name
            state = {v: defs - {var_name} for v, defs in state.items()}
            # Add the current definition
            state[var_name] = {node}
        return state

    def merge(self, states):
        return set.union(*states)

    def compare(self, state1, state2):
        return state1 == state2
    
    def gen_function(self, expr: Expression) -> Set[str]:
        if isinstance(expr, Assignment):
            return {expr.name}
        elif isinstance(expr, BinaryOperation):
            return self.gen_function(expr.left) | self.gen_function(expr.right)
        else:
            return set()

    def kill_function(self, expr: Expression) -> Set[str]:
        if isinstance(expr, Variable):
            return {expr.name}
        else:
            return set()      

    def create_nodes(self, stmt: Statement) -> [Node]:
        #last_label = self.label
        self.label = self.label + 1
        node = Node()
        node.label = self.label
        self.list_of_nodes.append(node)
        if isinstance(stmt, Assignment):
            #should i use a gen function for statement and one for expression?
            node.gen = self.gen_function(stmt.expression)
            node.kill = self.kill_function(stmt.variable)
            #trying something
            node.stmt = stmt
            node.exit = node.gen | (node.entry - node.kill)
        elif isinstance(stmt, WhileLoop):
            node.gen = self.gen_function(stmt.condition)
            # Create a node for the while loop body
            for body_stmt in stmt.body:
                body_node = self.create_nodes(body_stmt)
                #need to iterate through body_node which might 
                # be a list?
                node.successors.append(body_node)
                body_node.predecessors.append(node)
            # The last node in the body has a successor of the while loop node itself to represent the loop
            if node.successors:
                node.successors[-1].successors.append(node)
        elif isinstance(stmt, IfThenElse):
            node.gen = self.gen_function(stmt.condition)
            true_node = self.create_nodes(CompoundStatement(stmt.true_branch))
            false_node = self.create_nodes(CompoundStatement(stmt.false_branch))
            node.successors.extend([true_node, false_node])
            true_node.predecessors.append(node)
            false_node.predecessors.append(node)
        elif isinstance(stmt, CompoundStatement):
            for inner_stmt in stmt.statements:
                inner_node = self.create_nodes(inner_stmt)
                node.successors.append(inner_node)
                node = inner_node
        return self.list_of_nodes  

    #chaotic iteration
    def analyze(self, node: Node, live: Set[str]):
        # Initialize the state for the entry node
        node.entry_state = {v: set() for v in live}
        # Initialize the state for the exit node
        node.exit_state = node.entry_state.copy()
        # Apply the transfer function to update the state for the entry node
        node.entry_state = self.transfer_function(node, node.entry_state)
        # Propagate the state to the successors
        for succ in node.successors:
            # Merge the states from all predecessors
            pred_states = [pred.exit_state for pred in succ.predecessors]
            succ.entry_state = self.merge(pred_states)
            # Apply the transfer function to update the state for the successor
            succ.entry_state = self.transfer_function(succ, succ.entry_state)
            # Check if the state has changed
            if not self.compare(succ.entry_state, succ.exit_state):
                # Update the state and propagate the change
                succ.exit_state = succ.entry_state.copy()
                self.analyze(succ, live)

    def print_nodes(self, node, nodes, visited=None, level=0):
        return super().print_nodes(node, nodes, visited=None, level=0)

def main():
    # Uncomment below to test programs
    #unittest.main() 

    # Create the initial state
    initial_state = set()
    # Create the analysis object
    analysis = ReachingDefinitions(initial_state)
    # Create the nodes from the program
    nodes = analysis.create_nodes(increment_loop)
    # Create the control flow graph
    analysis.create_cfg()
    # Perform the analysis
    analysis.analyze(nodes)
    # Copy the nodes to print
    nodes_to_print = nodes.copy()
    # Print out the results
    analysis.print_nodes(None, nodes_to_print)

if __name__ == "__main__":
    main()