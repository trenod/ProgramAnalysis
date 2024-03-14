class Node:
    def __init__(self):
        self.label = None   # Label for this node in the control flow graph
        self.stmt = None    # Statement represented by this node
        self.expression = None # Expression represented by this node
        self.gen = set()    # Expressions generated in this node
        self.kill = set()   # Expressions killed in this node
        self.entry = set()  # Assignments live at entry to this node
        self.exit = set()   # Assignments live at exit from this node
        self.coming_in: list(Node) = [] # List of nodes coming in from in the control flow graph
        self.going_out: list(Node) = [] # List of nodes going out to in the control flow graph
        #self.entry_state = set()  # Analysis state at entry to this node (used for chaotic iteration)
        #self.exit_state = set()  # Analysis state at exit from this node (used for chaotic iteration)

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current
            current = current.next

    def is_exit(self):
        return self.going_out == []

    def add_predecessor(self, pred_node):
        """Add a predecessor node and automatically update the coming_in list."""
        if pred_node not in self.coming_in:
            self.coming_in.append(pred_node)
        if self not in pred_node.going_out:
            pred_node.going_out.append(self)
            

    # this function not needed? (logic already in above function)
    def add_successor(self, succ_node):
        """Add a successor node and automatically update the going_out list."""
        if succ_node not in self.going_out:
            self.going_out.append(succ_node)
            succ_node.coming_in.append(self)
            self.going_out.append(succ_node)

    def __repr__(self):
        return f"Node(label={self.label})"

    '''
    def __repr__(self):
        return f"Node(entry={self.entry}, exit={self.exit})"
    '''