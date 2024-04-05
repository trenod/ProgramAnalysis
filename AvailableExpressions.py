import logging
from collections import abc
from typing import List, Union, Callable, Set
from syntax import *
from examples import *
from node import *


# Available Expressions Analysis
class AvailableExpressionsAnalysis:

    def __init__(self) -> None:
        self.FV: list[(Statement.variable)] = [] #list of assignments with corresponding label, stored as Assignment for parsing Variable and Expression
        self.expressions: dict[(int, BinaryOperation)] = {} #dict of expressions/conditions with corresponding label, stored as BinaryOperation for parsing Variable and Expression
        self.assignments: dict[(int, Statement)] = {} #dict of assignments with corresponding label, stored as Assignment for parsing Variable and Expression
        self.label = 1
        #self.previous_node_label = 0
        self.previous_node: Node = None
        self.nodes = {}
    
    # Dealing with expressions
    def create_cfg_expression(self, expr) -> Node:
        if isinstance(expr, Variable):
            assert isinstance(expr.name, str)
        elif isinstance(expr, Constant):
            assert isinstance(expr.value, int)
        elif isinstance(expr, BinaryOperation):
            # Create a node for the expression
            node = Node()
            self.label = self.label + 1
            node.label = self.label
            node.expression = expr
            return node

    # Dealing with statements (using function above as helper function for expressions)
    def create_cfg_statement(self, stmt) -> (Node, list[Node]):
        node = Node()
        node.label = self.label  # str(self.label)+str(stmt.__class__)
        node.going_out = []
        # self.nodes.append(self.node)
        if isinstance(stmt, Skip):
            node.stmt = stmt
            logging.debug("Skip Node created: ", node.label, "\n")
            return node, [node]
        elif isinstance(stmt, Assignment):
            node.stmt = stmt
            logging.debug("Stmt Node created: ", node.label, "\n")
            return node, [node]
        elif isinstance(stmt, WhileLoop):
            # diamond with two exits
            condition = self.create_cfg_expression(stmt.condition)
            (root, exits) = self.create_cfg_statement(stmt.body)
            node.expression = condition.expression
            node.going_out = [root]
            for i in exits:
                # Careful, don't overwrite, append!
                i.going_out.append(node)
            return node, [node]
        elif isinstance(stmt, IfThenElse):
            self.create_cfg_expression(stmt.condition)
            (branch_t, exits_t) = self.create_cfg_statement(stmt.true_branch)
            (branch_f, exits_f) = self.create_cfg_statement(stmt.false_branch)
            node.going_out = [branch_f, branch_t]
            return node, node.going_out
        elif isinstance(stmt, CompoundStatement):
            # Doesn't actually use the first few self.*-lines above!
            first = None
            prevs = None
            for s in stmt.statements:
                (node, exits) = self.create_cfg_statement(s)
                #self.previous_node_label = self.label
                self.label = self.label + 1
                if first is None:
                    first = node
                if prevs is not None:
                    for p in prevs:
                        p.going_out.append(node)
                prevs = exits
            assert first is not None, "Empty CompoundStmt :-("
            return first, exits
        else:
            assert False, stmt
                
    def analyze(self, nodes: dict): #nodes: list of nodes, cfg: control flow graph
        for node in nodes.values():
            if self.previous_node is not None:
                node.entry = self.previous_node.exit
            if node.expression is not None:
                if node.expression in self.expressions.values():
                    node.gen.add(node.expression)

            elif node.stmt is not None:
                if node.stmt.variable not in self.FV:
                    self.FV.append(node.stmt.variable)
                    self.assignments[node.label] = node.stmt
                    node.gen.add(node.stmt)
                else:
                    node.kill.add(node.stmt)
            diff = node.entry.difference(node.kill)
            #print(f"Diff type: {type(diff)}")
            #print(f"Node.exit type: {type(node.exit)}")
            #print(f"Node.gen type: {type(node.gen)}")
            node.exit = node.gen.union(diff)
            #node.exit = node.gen.union(node.entry.difference(node.kill))
            self.previous_node = node

    def print_analysis_results(self, nodes : dict, cfg : list):
        print("Available Expressions Analysis \n")
        print(f"for program with control flow graph: {cfg}\n")
        for node in nodes.values():
            print(f"Node {node.label}: \n\n entry={node.entry}\n\n exit={node.exit}\n\n\n")
                
    def print_nodes(self, nodes : dict, cfg : list):
        print("Control Flow Graph: ")
        print(f"{cfg}\n")

        for node in nodes.values():
            print(f"Node {node.label}: Predecessors={node.coming_in} Successors={node.going_out} gen={node.gen}, kill={node.kill}, entry={node.entry}, exit={node.exit}\n")

    def mkDFS(self, node: Node, seen: Set[Node]): # -> List[(int,int)]:
        output = []
        if node in seen:
            return output
        seen.add(node)
        if node.label not in self.nodes:
            self.nodes[node.label] = node

        for i in node.going_out:
            if i.label not in self.nodes:
                self.nodes[i.label] = i
            output.append((node.label, i.label))
            output = output + self.mkDFS(i, seen)
        return output


def main():
    #Available expressions analysis:
    analysis = AvailableExpressionsAnalysis()

    '''
    # Analysis pipeline for available expressions
    for program in [book_example, increment_loop, conditional_assignment, nested_loops, while_with_conditional]:
        (root, exits) = analysis.create_cfg_statement(program)
        # Need a final patch-up!
        the_exit = Node()
        the_exit.label = "exit"
        the_exit.going_out = []
        for e in exits:
            e.going_out.append(the_exit)
        analysis.nodes[len(analysis.nodes)] = the_exit
        cfg = (analysis.mkDFS(root, set()))
        analysis.analyze(analysis.nodes)

        analysis.print_nodes(analysis.nodes, cfg)
    '''

    
    # Create the CFG, with nodes containing necessary information for doing an analysis
    (root, exits) = analysis.create_cfg_statement(book_example)
    print(root, exits)

    # Need a final patch-up!
    the_exit = Node()
    the_exit.label = "exit"
    the_exit.going_out = []
    for e in exits:
        e.going_out.append(the_exit)
    analysis.nodes[len(analysis.nodes)] = the_exit

    cfg = (analysis.mkDFS(root, set()))
    #print(cfg)
    # assert that the result is right.
    assert (cfg == [(1, 2), (2, 3), (3, 4), (4,5), (5, 3), (3, 'exit')])
    #exit(1)

    # Analyze the program
    analysis.analyze(analysis.nodes)

    # Print the results
    analysis.print_analysis_results(analysis.nodes, cfg)
    
    

if __name__ == "__main__":
    main()