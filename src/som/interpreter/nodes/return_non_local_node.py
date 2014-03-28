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
        ctx_frame = self.determine_context(frame)
        marker = ctx_frame.get_on_stack_marker()

        if marker.is_on_stack():
            result = self._expr.execute(frame)
            raise ReturnException(result, marker)
        else:
            block      = frame.get_self()
            outer_self = ctx_frame.get_self()
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
        marker = frame.init_and_get_on_stack_marker()
        try:
            result = self._method_body.execute(frame)
        except ReturnException as e:
            if not e.has_reached_target(marker):
                raise e
            else:
                return e.get_result()
        finally:
            marker.frame_no_longer_on_stack()
        return result

    def execute_void(self, frame):
        marker = frame.init_and_get_on_stack_marker()
        try:
            self._method_body.execute_void(frame)
        except ReturnException as e:
            if not e.has_reached_target(marker):
                raise e
        finally:
            marker.frame_no_longer_on_stack()
