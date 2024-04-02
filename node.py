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

    def __repr__(self):
        return f"Node(label={self.label})"
    
    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.label == other.label
        return False