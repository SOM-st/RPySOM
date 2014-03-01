from .expression_node import ExpressionNode

from rpython.rlib.jit import unroll_safe


class GenericMessageNode(ExpressionNode):

    _immutable_fields_ = ['_selector', '_universe',
                          '_rcvr_expr?', '_arg_exprs?[*]']
    _child_nodes_      = ['_rcvr_expr',  '_arg_exprs[*]']

    def __init__(self, selector, universe, rcvr_expr, arg_exprs,
                 source_section = None):
        ExpressionNode.__init__(self, source_section)
        self._selector = selector
        self._universe = universe
        self._rcvr_expr = self.adopt_child(rcvr_expr)
        self._arg_exprs = self.adopt_children(arg_exprs)

    @unroll_safe
    def execute(self, frame):
        rcvr = self._rcvr_expr.execute(frame)
        if self._arg_exprs:
            args = [arg_exp.execute(frame) for arg_exp in self._arg_exprs]
        else:
            args = None
        return self.execute_evaluated(frame, rcvr, args)

    def execute_evaluated(self, frame, rcvr, args):
        method = self._lookup_method(rcvr)
        return method.invoke(frame, rcvr, args)

    def _lookup_method(self, rcvr):
        rcvr_class = self._class_of_receiver(rcvr)
        return rcvr_class.lookup_invokable(self._selector)

    def _class_of_receiver(self, rcvr):
        if self._rcvr_expr.is_super_node():
            return self._rcvr_expr.get_super_class()
        return rcvr.get_class(self._universe)
