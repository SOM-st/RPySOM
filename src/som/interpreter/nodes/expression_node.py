from rtruffle.node import Node


class ExpressionNode(Node):

    def __init__(self, source_section = None):
        Node.__init__(self, source_section)

    def execute(self, frame):
        pass

    def is_super_node(self):
        return False
