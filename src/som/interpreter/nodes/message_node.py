from .expression_node import ExpressionNode
from rpython.rlib import jit

from rpython.rlib.jit import unroll_safe, set_param


def get_printable_location(method):
    #assert isinstance(method, Method)
    #return "send %s" % method.merge_point_string()
    return "SEND TODO"


# jitdriver = jit.JitDriver(
#     greens=['method'],
#     reds= 'auto', #['frame'],
#     #virtualizables=['frame'],
#     get_printable_location=get_printable_location,
#     should_unroll_one_iteration = lambda method: True)
#
#
# def jitpolicy(driver):
#     from rpython.jit.codewriter.policy import JitPolicy
#     return JitPolicy()
#
# set_param(jitdriver, 'threshold', 16199)
# set_param(jitdriver, 'function_threshold', 26199)


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
        if method:
            #jitdriver.jit_merge_point(method = method)  # , frame = frame
            return method.invoke(frame, rcvr, args)
        else:
            return rcvr.send_does_not_understand(frame, self._selector, args,
                                                 self._universe)

    def _lookup_method(self, rcvr):
        rcvr_class = self._class_of_receiver(rcvr)
        return rcvr_class.lookup_invokable(self._selector)

    def _class_of_receiver(self, rcvr):
        if self._rcvr_expr.is_super_node():
            return self._rcvr_expr.get_super_class()
        return rcvr.get_class(self._universe)

    def __str__(self):
        return "%s(%s, %s)" % (self.__class__.__name__,
                               self._selector,
                               self._source_section)
