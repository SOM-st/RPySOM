from ..expression_node import ExpressionNode
from .to_do_node       import AbstractToDoNode

from rpython.rlib import jit

from som.vmobjects.method import Method


class AbstractToByDoNode(AbstractToDoNode):

    _immutable_fields_ = ['_step_expr?']
    _child_nodes_      = ['_step_expr' ]

    def __init__(self, rcvr_expr, limit_expr, step_expr, body_expr, universe,
                 source_section = None):
        AbstractToDoNode.__init__(self, rcvr_expr, limit_expr, body_expr,
                                  universe, source_section)
        self._step_expr  = self.adopt_child(step_expr)

    def execute(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        limit = self._limit_expr.execute(frame)
        step  = self._step_expr.execute(frame)
        body  = self._body_expr.execute(frame)
        return self._to_by_loop(frame, rcvr, limit, step, body)

    def execute_evaluated(self, frame, rcvr, args):
        return self._to_by_loop(frame, rcvr, args[0], args[1], args[2])


def get_printable_location(block_method):
    assert isinstance(block_method, Method)
    return "#to:do: %s" % block_method.merge_point_string()


int_driver = jit.JitDriver(
    greens=['block_method'],
    reds='auto',
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)


class IntToIntByDoNode(AbstractToByDoNode):

    def _to_by_loop(self, frame, rcvr, limit, step, body_block):
        block_method = body_block.get_method()

        i   = rcvr.get_embedded_integer()
        top = limit.get_embedded_integer()
        by  = step.get_embedded_integer()
        while i <= top:
            int_driver.jit_merge_point(block_method = block_method)
            block_method.invoke(frame, body_block,
                                [self._universe.new_integer(i)])
            i += by
        return rcvr


double_driver = jit.JitDriver(
    greens=['block_method'],
    reds='auto',
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)


class IntToDoubleByDoNode(AbstractToByDoNode):

    def _to_by_loop(self, frame, rcvr, limit, step, body_block):
        block_method = body_block.get_method()

        i   = rcvr.get_embedded_integer()
        top = limit.get_embedded_double()
        by  = step.get_embedded_integer()
        while i <= top:
            double_driver.jit_merge_point(block_method = block_method)
            block_method.invoke(frame, body_block,
                                [self._universe.new_integer(i)])
            i += by
        return rcvr
