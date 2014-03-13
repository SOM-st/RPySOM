from ..expression_node import ExpressionNode
from rpython.rlib import jit
from som.vmobjects.method import Method


class AbstractToDoNode(ExpressionNode):

    _immutable_fields_ = ['_rcvr_expr?', '_limit_expr?', '_body_expr?',
                          '_universe']
    _child_nodes_      = ['_rcvr_expr', '_limit_expr', '_body_expr']

    def __init__(self, rcvr_expr, limit_expr, body_expr, universe,
                 source_section = None):
        ExpressionNode.__init__(self, source_section)
        self._rcvr_expr  = self.adopt_child(rcvr_expr)
        self._limit_expr = self.adopt_child(limit_expr)
        self._body_expr  = self.adopt_child(body_expr)
        self._universe   = universe

    def execute(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        limit = self._limit_expr.execute(frame)
        body  = self._body_expr.execute(frame)
        self._do_loop(frame, rcvr, limit, body)
        return rcvr

    def execute_void(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        limit = self._limit_expr.execute(frame)
        body  = self._body_expr.execute(frame)
        self._do_loop(frame, rcvr, limit, body)

    def execute_evaluated(self, frame, rcvr, args):
        self._do_loop(frame, rcvr, args[0], args[1])
        return rcvr

    def execute_evaluated_void(self, frame, rcvr, args):
        self._do_loop(frame, rcvr, args[0], args[1])


def get_printable_location(block_method):
    assert isinstance(block_method, Method)
    return "#to:do: %s" % block_method.merge_point_string()


int_driver = jit.JitDriver(
    greens=['block_method'],
    reds='auto',
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)


class IntToIntDoNode(AbstractToDoNode):

    def _do_loop(self, frame, rcvr, limit, body_block):
        block_method = body_block.get_method()

        i   = rcvr.get_embedded_integer()
        top = limit.get_embedded_integer()
        while i <= top:
            int_driver.jit_merge_point(block_method = block_method)
            block_method.invoke_void(frame, body_block,
                                     [self._universe.new_integer(i)])
            i += 1


double_driver = jit.JitDriver(
    greens=['block_method'],
    reds='auto',
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)


class IntToDoubleDoNode(AbstractToDoNode):

    def _do_loop(self, frame, rcvr, limit, body_block):
        block_method = body_block.get_method()

        i   = rcvr.get_embedded_integer()
        top = limit.get_embedded_double()
        while i <= top:
            double_driver.jit_merge_point(block_method = block_method)
            block_method.invoke_void(frame, body_block,
                                     [self._universe.new_integer(i)])
            i += 1
