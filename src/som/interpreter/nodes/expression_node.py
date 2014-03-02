from rtruffle.node import Node, initialize_node_class


class ExpressionNode(Node):

    def __init__(self, source_section = None):
        Node.__init__(self, source_section)

    def execute(self, frame):
        pass

    def is_super_node(self):
        return False


initialize_node_class(ExpressionNode)
