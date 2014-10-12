from .contextual_node import ContextualNode
from .expression_node import ExpressionNode

from ..control_flow   import ReturnException


class ReturnNonLocalNode(ContextualNode):

    _immutable_fields_ = ['_expr?', '_universe']
    _child_nodes_      = ['_expr']

    def __init__(self, context_level, expr, universe, source_section = None):
        ContextualNode.__init__(self, context_level, source_section)
        self._expr     = self.adopt_child(expr)
        self._universe = universe

    def execute(self, frame):
        result = self._expr.execute(frame)
        block = self.determine_block(frame)

        if block.is_outer_on_stack():
            raise ReturnException(result, block.get_on_stack_marker())
        else:
            block      = frame.get_self()
            outer_self = block.get_outer_self()
            return outer_self.send_escaped_block(block, self._universe)

    def execute_void(self, frame):
        self.execute(frame)


class CatchNonLocalReturnNode(ExpressionNode):

    _immutable_fields_ = ['_method_body?']
    _child_nodes_      = ['_method_body']

    def __init__(self, method_body, source_section = None):
        ExpressionNode.__init__(self, source_section)
        self._method_body = self.adopt_child(method_body)

    def execute(self, frame):
        marker = frame.get_on_stack_marker()
        try:
            return self._method_body.execute(frame)
        except ReturnException as e:
            if not e.has_reached_target(marker):
                raise e
            else:
                return e.get_result()
        finally:
            marker.mark_as_no_longer_on_stack()

    def execute_void(self, frame):
        marker = frame.get_on_stack_marker()
        try:
            self._method_body.execute_void(frame)
        except ReturnException as e:
            if not e.has_reached_target(marker):
                raise e
        finally:
            marker.mark_as_no_longer_on_stack()
