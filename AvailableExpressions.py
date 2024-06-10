import logging
from collections import abc
from typing import List, Union, Callable, Set
from syntax import *
from examples import *
from node import *
#import pdb; pdb.set_trace()

#logging.basicConfig(filename='AEAnalysis.log', level=logging.DEBUG)


# Available Expressions Analysis
class AvailableExpressionsAnalysis:

    def __init__(self) -> None:
        self.FV: dict[(Statement.variable, Statement.expression)] = {} #dict of assignments variables with corresponding expression, stored as Assignment for parsing Variable and Expression
        self.expressions: dict[(int, BinaryOperation)] = {} #dict of expressions/conditions with corresponding label, stored as BinaryOperation for parsing Variable and Expression
        self.assignments: dict[(int, Statement)] = {} #dict of assignments with corresponding label, stored as Assignment for parsing Variable and Expression
        self.label = 1
        #self.previous_node_label = 0
        self.previous_node: Node = None
        self.nodes = {}
        self.kill: dict[(Node, BinaryOperation)] = {} #dict of expressions/conditions with corresponding label, stored as BinaryOperation for parsing Variable and Expression
        self.gen: dict[(Node, BinaryOperation)] = {} #dict of expressions/conditions with corresponding label, stored as BinaryOperation for parsing Variable and Expression
    
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
                
    def analyze(self, nodes: dict, cfg): #nodes: list of nodes, cfg: control flow graph
        # Now we need to iterate over the nodes to find the entry and exit sets
        # for each node. We can do this by iterating over the nodes in the CFG
        # and updating the entry and exit sets until they don't change anymore.
        # This is called chaotic iteration.

        # TODO: Use the CFG to iterate over the nodes in the right order
        cfglist = []
        nodelist = {}
        for elem in cfg:
            print(f"CFG element: {elem}")
            (fst, snd) = elem
            cfglist.append(fst)
            cfglist.append(snd)
        cfglist.remove('exit')

        for elem in cfglist:
            for node in nodes.values():
                if node.label == elem:
                    nodelist[node.label] = node

        changed = True
        onechange = False
        killed = False
        iterationcount = 0 #for debugging
        while (changed):
            iterationcount += 1
            print(f"Iteration {iterationcount}")
            for node in nodelist.values(): #nodes.values():
                if self.previous_node is not None:
                    node.entry = self.previous_node.exit
                else:
                    node.entry = set()
                '''
                if node.expression is not None:
                    if node.expression in self.expressions.values() and node.expression not in node.gen:
                        node.gen.add(node.expression)
                        onechange = True
                '''
                if node.stmt is not None:
                    if node.stmt.variable not in self.FV.keys():
                        self.FV[node.stmt.variable] = node.stmt.expression
                        #self.assignments[node.label] = node.stmt
                        node.gen.add(node.stmt.expression)
                        self.gen[node] = node.stmt.expression
                        onechange = True
                    elif node.stmt.variable in self.FV.keys():
                        if node.stmt.expression not in node.kill and node.stmt.expression in self.FV.values():
                            node.kill.add(node.stmt.expression)
                            self.kill[node] = node.stmt.expression
                            #for key, value in self.FV.items():
                             #   if value == node.stmt.expression:
                              #      self.FV[key] = None
                                    #self.kill.add(node.stmt.expression)
                               #     onechange = True
                            #print(list(nodelist.keys())[list(nodelist.values()).index(16)])
                            #self.FV[node.stmt.variable] = None
                            #self.kill.add(node.stmt.expression)
                            onechange = True
                diff = node.entry.difference(node.kill)
                # TODO: Take node.going_out / node.coming_in into account
                #print(f"Diff type: {type(diff)}")
                #print(f"Node.exit type: {type(node.exit)}")
                #print(f"Node.gen type: {type(node.gen)}")
                node.exit = node.gen.union(diff)
                #node.exit = node.gen.union(node.entry.difference(node.kill))
                if (killed):
                    for node in nodelist.values():
                        if node.stmt.expression in self.kill:
                            node.kill.add(node.stmt.expression)
                            killed = False

                self.previous_node = node
            self.previous_node = None
            if not onechange:
                print("No change in this iteration (are we done?)")
                changed = False
            else:
                print("One or more changes in this iteration")
                onechange = False
        print("Analysis done")

    def print_analysis_results(self, nodes : dict, cfg : list):
        print("Available Expressions Analysis \n")
        print(f"for program with control flow graph: {cfg}\n")
        print("Nodes in the program: \n\n")
        for node in nodes.values():
            print(f"Node: {node.label}\n")

        print("\n\n\n")
        print("Results: \n\n")
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
        print(f"exit: {e}")
        e.going_out.append(the_exit)
    #analysis.nodes[len(analysis.nodes)] = the_exit

    cfg = (analysis.mkDFS(root, set()))
    #print(cfg)
    # assert that the result is right.
    assert (cfg == [(1, 2), (2, 3), (3, 4), (4,5), (5, 3), (3, 'exit')])
    #exit(1)

    # Analyze the program
    analysis.analyze(analysis.nodes, cfg)

    # Print the results
    analysis.print_analysis_results(analysis.nodes, cfg)
    
    

if __name__ == "__main__":
    main()