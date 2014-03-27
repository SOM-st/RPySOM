from ..expression_node   import ExpressionNode
from ....vmobjects.block import Block


class IfTrueIfFalseNode(ExpressionNode):

    _immutable_fields_ = ['_rcvr_expr?', '_true_expr?', '_false_expr?',
                          '_universe']
    _child_nodes_      = ['_rcvr_expr',  '_true_expr',  '_false_expr']

    def __init__(self, rcvr_expr, true_expr, false_expr, universe,
                 source_section):
        ExpressionNode.__init__(self, source_section)
        self._rcvr_expr  = self.adopt_child(rcvr_expr)
        self._true_expr  = self.adopt_child(true_expr)
        self._false_expr = self.adopt_child(false_expr)
        self._universe   = universe

    def execute(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        true  = self._true_expr.execute(frame)
        false = self._false_expr.execute(frame)

        return self._do_iftrue_iffalse(rcvr, true, false)

    def execute_evaluated(self, frame, rcvr, args):
        return self._do_iftrue_iffalse(rcvr, args[0], args[1])

    def _value_of(self, obj):
        if isinstance(obj, Block):
            return obj.get_method().invoke(obj, None)
        else:
            return obj

    def _do_iftrue_iffalse(self, rcvr, true, false):
        if rcvr is self._universe.trueObject:
            return self._value_of(true)
        else:
            assert rcvr is self._universe.falseObject
            return self._value_of(false)

    def execute_void(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        true  = self._true_expr.execute(frame)
        false = self._false_expr.execute(frame)

        return self._do_iftrue_iffalse_void(rcvr, true, false)

    def execute_evaluated_void(self, frame, rcvr, args):
        return self._do_iftrue_iffalse_void(rcvr, args[0], args[1])

    def _value_of_void(self, obj):
        if isinstance(obj, Block):
            obj.get_method().invoke_void(obj, None)

    def _do_iftrue_iffalse_void(self, rcvr, true, false):
        if rcvr is self._universe.trueObject:
            self._value_of_void(true)
        else:
            assert rcvr is self._universe.falseObject
            self._value_of_void(false)



class IfNode(ExpressionNode):

    _immutable_fields_ = ['_rcvr_expr?', '_branch_expr?', '_condition',
                          '_universe']
    _child_nodes_      = ['_rcvr_expr',  '_branch_expr']

    def __init__(self, rcvr_expr, branch_expr, condition_obj, universe,
                 source_section):
        ExpressionNode.__init__(self, source_section)
        self._rcvr_expr   = self.adopt_child(rcvr_expr)
        self._branch_expr = self.adopt_child(branch_expr)
        self._condition   = condition_obj
        self._universe    = universe

    def execute(self, frame):
        rcvr   = self._rcvr_expr.execute(frame)
        branch = self._branch_expr.execute(frame)
        return self._do_if(rcvr, branch)
    
    def execute_void(self, frame):
        rcvr   = self._rcvr_expr.execute(frame)
        branch = self._branch_expr.execute(frame)
        return self._do_if_void(rcvr, branch)

    def execute_evaluated(self, frame, rcvr, args):
        return self._do_if(rcvr, args[0])
    
    def execute_evaluated_void(self, frame, rcvr, args):
        return self._do_if_void(rcvr, args[0])

    def _value_of(self, obj):
        if isinstance(obj, Block):
            return obj.get_method().invoke(obj, None)
        else:
            return obj
    
    def _value_of_void(self, obj):
        if isinstance(obj, Block):
            obj.get_method().invoke_void(obj, None)

    def _do_if(self, rcvr, branch):
        if rcvr is self._condition:
            return self._value_of(branch)
        else:
            assert (rcvr is self._universe.falseObject or
                    rcvr is self._universe.trueObject)
            return self._universe.nilObject
        
    def _do_if_void(self, rcvr, branch):
        if rcvr is self._condition:
            self._value_of_void(branch)
        else:
            assert (rcvr is self._universe.falseObject or
                    rcvr is self._universe.trueObject)
