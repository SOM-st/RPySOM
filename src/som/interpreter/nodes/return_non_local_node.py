from .contextual_node import ContextualNode
from .expression_node import ExpressionNode

from ..control_flow   import ReturnException
from rtruffle.node import initialize_node_class


class ReturnNonLocalNode(ContextualNode):

    _immutable_fields_ = ['_expr?', '_universe']
    _child_nodes_      = ['_expr']

    def __init__(self, context_level, expr, universe, source_section = None):
        ContextualNode.__init__(self, context_level, source_section)
        self._expr     = self.adopt_child(expr)
        self._universe = universe

    def execute(self, frame):
        ctx_frame = self.determine_context(frame)

        if ctx_frame.is_on_stack():
            result = self._expr.execute(frame)
            raise ReturnException(result, ctx_frame)
        else:
            block      = frame.get_self()
            outer_self = ctx_frame.get_self()
            return outer_self.send_escaped_block(frame, block, self._universe)


class CatchNonLocalReturnNode(ExpressionNode):

    _immutable_fields_ = ['_method_body?']
    _child_nodes_      = ['_method_body']

    def __init__(self, method_body, source_section = None):
        ExpressionNode.__init__(self, source_section)
        self._method_body = self.adopt_child(method_body)

    def execute(self, frame):
        try:
            result = self._method_body.execute(frame)
        except ReturnException as e:
            if not e.has_reached_target(frame):
                raise e
            else:
                return e.get_result()
        finally:
            frame.mark_as_no_longer_on_stack()
        return result


initialize_node_class(ReturnNonLocalNode)
initialize_node_class(CatchNonLocalReturnNode)
