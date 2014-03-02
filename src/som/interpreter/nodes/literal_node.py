from .expression_node import ExpressionNode
from rtruffle.node import initialize_node_class


class LiteralNode(ExpressionNode):

    _immutable_fields_ = ["_value"]

    def __init__(self, value, source_section = None):
        ExpressionNode.__init__(self, source_section)
        self._value = value

    def execute(self, frame):
        return self._value


initialize_node_class(LiteralNode)
