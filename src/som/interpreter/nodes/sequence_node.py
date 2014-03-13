from .expression_node import ExpressionNode

from rpython.rlib.jit import unroll_safe


class SequenceNode(ExpressionNode):

    _immutable_fields_ = ['_exprs?[*]']
    _child_nodes_      = ['_exprs[*]']

    def __init__(self, expressions, source_section = None):
        ExpressionNode.__init__(self, source_section)
        self._exprs = self.adopt_children(expressions)

    @unroll_safe
    def execute(self, frame):
        result = None
        for expr in self._exprs:
            result = expr.execute(frame)
        return result
