import logging
from collections import abc
from typing import List, Union, Callable, Set
from syntax import *
from examples import *
from node import *


# Available Expressions Analysis
class AvailableExpressionsAnalysis:

    def __init__(self) -> None:
        self.FV: list[(Assignment, int)] = [] #list of assignments with corresponding label, stored as Assignment for parsing Variable and Expression
        #self.label = 0
        #self.cfg: list[(int, int)] = []
        self.nodes: list[Node] = []
        #self.previous_node_label = 0
        #self.if_then_else = False
        #self.while_loop = False
        #self.is_first_node_in_while = False
        #self.is_last_node_in_while = False
        #self.first_node_in_while: list[Node] = []
        #self.first_node = None
        #self.was_last_node_in_while = False
        #self.last_node_in_while: list[Node] = []
        #self.node = None
        #self.last_node = None
        #self.current_node = None
        #self.previous_node = None
        #self.expr_node = False
        #self.node_created = False

    # Create the CFG as well as the nodes containing necessary information for doing an analysis (can later move to superclass)
    #def create_cfg(self, program: Statement) -> list((int, int)):
    #    assert isinstance(program, CompoundStatement)
    #    for stmt in program.statements:
    #        self.create_cfg_statement(stmt)
    #    return self.cfg
    
    # Dealing with expressions
    def create_cfg_expression(self, expr, label: int) -> (Node, label):
        if isinstance(expr, Variable):
            assert isinstance(expr.name, str)
        elif isinstance(expr, Constant):
            assert isinstance(expr.value, int)
        elif isinstance(expr, BinaryOperation):
            # Create a node for the expression
            node = Node()
            if (label == None):
                label = 0
            label = label + 1
            node.label = label
            node.expression = expr
            self.nodes.append(node)
            logging.debug("Binary operation Node created: ", self.node.label, "\n")
            return (node, label)

    # Dealing with statements (using function above as helper function for expressions)
    def create_cfg_statement(self, stmt, label: int) -> (Node, list[Node], label):
        node = Node()
        if (label == None):
            label = 0
        label = label + 1
        node.label = label  # str(self.label)+str(stmt.__class__)
        node.going_out = []
        # self.nodes.append(self.node)
        if isinstance(stmt, Assignment):
            node.stmt = stmt
            logging.debug("Stmt Node created: ", node.label, "\n")
            return node, [node], label
        elif isinstance(stmt, WhileLoop):
            # diamond with two exits
            # TODO: self.create_cfg_expression(stmt.condition)
            # Placing condition node first in while loop/nodes, check if it's correct
            (condition_node, label) = self.create_cfg_expression(stmt.condition, label)
            (root, exits, label) = self.create_cfg_statement(stmt.body, label)
            node.going_out = [condition_node]
            exits.append(root)

            #(root, exits, label) = self.create_cfg_statement(stmt.body, label)
            #node.going_out = [root]
            for i in exits:
                # Careful, don't overwrite, append!
                i.going_out.append(node)
            return node, [node], label
        elif isinstance(stmt, IfThenElse):
            self.create_cfg_expression(stmt.condition)
            (branch_t, exits_t) = self.create_cfg_statement(stmt.true_branch)
            (branch_f, exits_f) = self.create_cfg_statement(stmt.false_branch)
            node.going_out = [branch_f, branch_t]
            return node, node.going_out, label
        elif isinstance(stmt, CompoundStatement):
            # Doesn't actually use the first few self.*-lines above!
            first = None
            prevs = None
            for s in stmt.statements:
                (node, exits) = self.create_cfg_statement(s, label)
                if first is None:
                    first = node
                if prevs is not None:
                    for p in prevs:
                        p.going_out.append(node)
                prevs = exits
            assert first is not None, "Empty CompoundStmt :-("
            return first, exits, label
        else:
            assert False, stmt

    #this function is not needed currently
    def create_cfg_while(self, stmt):
        for i in range(0, len(stmt.body)):
            if (i == 0):
                self.create_cfg_expression(stmt.condition)
            elif (i == len(stmt.body) - 1):
                self.create_cfg_expression(stmt.body[i])
                self.create_cfg_statement(stmt.body[i])
                
    def analyze(self, nodes: list): #nodes: list of nodes, cfg: control flow graph
        for node in nodes:
            if node.expression is not None:
                if node.expression in self.FV:
                    node.gen = node.expression

            elif node.stmt is not None:
                if node.stmt not in self.FV:
                    self.FV.append((node.stmt, node.label))
                    node.gen = node.stmt
                else:
                    node.kill = node.stmt
                
    def print_nodes(self, nodes : list, cfg : list):
        print("Control Flow Graph: ")
        print(cfg)

        for node in nodes:
            print(f"Node {node.label}: Predecessors={node.coming_in} Successors={node.going_out} gen={node.gen}, kill={node.kill}, entry={node.entry}, exit={node.exit}")

    def print_cfg(self, cfg: list):
        print("Control Flow Graph: ")
        print(cfg)


def mkDFS(node: Node, seen: Set[Node]): # -> List[(int,int)]:
    output = []
    if node in seen:
        return output
    seen.add(node)

    for i in node.going_out:
        output.append((node.label, i.label))
        output = output + mkDFS(i, seen)
    return output


def main():
    #Available expressions analysis:
    analysis = AvailableExpressionsAnalysis()

    # Create the CFG, with nodes containing necessary information for doing an analysis
    (root, exits, nr_of_nodes) = analysis.create_cfg_statement(book_example, 0)
    print("Number of nodes: ", nr_of_nodes, "\n")
    print(root, exits)

    # Need a final patch-up!
    the_exit = Node()
    the_exit.label = "exit"
    the_exit.going_out = []
    for e in exits:
        e.going_out.append(the_exit)

    print(mkDFS(root, set()))
    # analysis.print_cfg(cfg)
    # TODO: assert that the result is right.
    exit(1)

    # Analyze the program
    nodes = analysis.nodes
    analysis.analyze(nodes)

    # Print the results
    analysis.print_nodes(nodes, cfg)

if __name__ == "__main__":
    main()