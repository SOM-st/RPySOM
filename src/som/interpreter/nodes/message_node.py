from .expression_node import ExpressionNode
from rpython.rlib.debug import make_sure_not_resized

from .specialized.if_true_false import IfTrueIfFalseNode, IfNode
from .specialized.to_do_node    import IntToIntDoNode, IntToDoubleDoNode
from .specialized.to_by_do_node import IntToIntByDoNode, IntToDoubleByDoNode
from .specialized.while_node    import WhileMessageNode

from rpython.rlib.jit import unroll_safe

from ...vmobjects.block   import Block
from ...vmobjects.double  import Double
from ...vmobjects.integer import Integer


class AbstractMessageNode(ExpressionNode):

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
    def _evaluate_rcvr_and_args(self, frame):
        rcvr = self._rcvr_expr.execute(frame)
        if self._arg_exprs:
            args = [arg_exp.execute(frame) for arg_exp in self._arg_exprs]
        else:
            args = None
        return rcvr, args


class UninitializedMessageNode(AbstractMessageNode):

    def execute(self, frame):
        rcvr, args = self._evaluate_rcvr_and_args(frame)
        return self._specialize(frame, rcvr, args).\
            execute_evaluated(frame, rcvr, args)

    def execute_void(self, frame):
        rcvr, args = self._evaluate_rcvr_and_args(frame)
        self._specialize(frame, rcvr, args).\
            execute_evaluated_void(frame, rcvr, args)

    def _specialize(self, frame, rcvr, args):
        if args:
            if isinstance(args[0], Block):
                if   self._selector.get_string() == "whileTrue:":
                    return self.replace(
                        WhileMessageNode(self._rcvr_expr, self._arg_exprs[0],
                                         self._universe.trueObject,
                                         self._universe, self._source_section))
                elif self._selector.get_string() == "whileFalse:":
                    return self.replace(
                        WhileMessageNode(self._rcvr_expr, self._arg_exprs[0],
                                         self._universe.falseObject,
                                         self._universe, self._source_section))
            if (isinstance(args[0], Integer) and isinstance(rcvr, Integer) and
                len(args) > 1 and isinstance(args[1], Block) and
                self._selector.get_string() == "to:do:"):
                return self.replace(
                    IntToIntDoNode(self._rcvr_expr, self._arg_exprs[0],
                                   self._arg_exprs[1], self._universe,
                                   self._source_section))
            if (isinstance(args[0], Double) and isinstance(rcvr, Integer) and
                len(args) > 1 and isinstance(args[1], Block) and
                self._selector.get_string() == "to:do:"):
                return self.replace(
                    IntToDoubleDoNode(self._rcvr_expr, self._arg_exprs[0],
                                      self._arg_exprs[1], self._universe,
                                      self._source_section))
            if (isinstance(args[0], Integer) and isinstance(rcvr, Integer) and
                len(args) == 3 and
                    isinstance(args[1], Integer) and
                    isinstance(args[2], Block) and
                self._selector.get_string() == "to:by:do:"):
                return self.replace(
                    IntToIntByDoNode(self._rcvr_expr, self._arg_exprs[0],
                                   self._arg_exprs[1], self._arg_exprs[2],
                                   self._universe, self._source_section))
            if (isinstance(args[0], Double) and isinstance(rcvr, Integer) and
                len(args) == 3 and
                    isinstance(args[1], Integer) and
                    isinstance(args[2], Block) and
                self._selector.get_string() == "to:by:do:"):
                return self.replace(
                    IntToDoubleByDoNode(self._rcvr_expr, self._arg_exprs[0],
                                      self._arg_exprs[1], self._arg_exprs[2],
                                      self._universe, self._source_section))
            if (len(args) == 2 and (rcvr is self._universe.trueObject or
                                    rcvr is self._universe.falseObject) and
                self._selector.get_string() == "ifTrue:ifFalse:"):
                return self.replace(
                    IfTrueIfFalseNode(self._rcvr_expr, self._arg_exprs[0],
                                      self._arg_exprs[1], self._universe,
                                      self._source_section))
            if (len(args) == 1 and (rcvr is self._universe.trueObject or
                                    rcvr is self._universe.falseObject)):
                if self._selector.get_string() == "ifTrue:":
                    return self.replace(
                        IfNode(self._rcvr_expr, self._arg_exprs[0],
                               self._universe.trueObject, self._universe,
                               self._source_section))
                if self._selector.get_string() == "ifFalse:":
                    return self.replace(
                        IfNode(self._rcvr_expr, self._arg_exprs[0],
                               self._universe.falseObject, self._universe,
                               self._source_section))
        return self.replace(
            GenericMessageNode(self._selector, self._universe, self._rcvr_expr,
                               self._arg_exprs, self._source_section))


class GenericMessageNode(AbstractMessageNode):

    def execute(self, frame):
        rcvr, args = self._evaluate_rcvr_and_args(frame)
        return self.execute_evaluated(frame, rcvr, args)

    def execute_void(self, frame):
        rcvr, args = self._evaluate_rcvr_and_args(frame)
        self.execute_evaluated_void(frame, rcvr, args)

    def execute_evaluated_void(self, frame, rcvr, args):
        assert args is not None
        make_sure_not_resized(args)
        method = self._lookup_method(rcvr)
        if method:
            method.invoke_void(rcvr, args)
        else:
            rcvr.send_does_not_understand_void(self._selector, args,
                                               self._universe)

    def execute_evaluated(self, frame, rcvr, args):
        assert args is not None
        make_sure_not_resized(args)
        method = self._lookup_method(rcvr)
        if method:
            return method.invoke(rcvr, args)
        else:
            return rcvr.send_does_not_understand(self._selector, args,
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
