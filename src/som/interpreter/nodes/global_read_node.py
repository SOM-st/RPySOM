from .expression_node import ExpressionNode
from som.vm.globals import nilObject


class UninitializedGlobalReadNode(ExpressionNode):

    _immutable_fields_ = ["_global_name", "_universe"]

    def __init__(self, global_name, universe, source_section = None):
        ExpressionNode.__init__(self, source_section)
        self._global_name = global_name
        self._universe    = universe

    def execute(self, frame):
        if self._universe.has_global(self._global_name):
            return self._specialize().execute(frame)
        else:
            return frame.get_self().send_unknown_global(self._global_name,
                                                        self._universe)

    def _specialize(self):
        glob = self._global_name.get_string()
        if glob == "true":
            cached = ConstantGlobalReadNode(self._universe.trueObject,
                                            self.get_source_section())
        elif glob == "false":
            cached = ConstantGlobalReadNode(self._universe.falseObject,
                                            self.get_source_section())
        elif glob == "nil":
            cached = ConstantGlobalReadNode(nilObject,
                                            self.get_source_section())
        else:
            assoc = self._universe.get_globals_association(self._global_name)
            cached = CachedGlobalReadNode(assoc, self.get_source_section())
        return self.replace(cached)


class CachedGlobalReadNode(ExpressionNode):

    _immutable_fields_ = ['_assoc']

    def __init__(self, assoc, source_section):
        ExpressionNode.__init__(self, source_section)
        self._assoc = assoc

    def execute(self, frame):
        return self._assoc.get_value()


class ConstantGlobalReadNode(ExpressionNode):

    _immutable_fields_ = ['_value']

    def __init__(self, value, source_section):
        ExpressionNode.__init__(self, source_section)
        self._value = value

    def execute(self, frame):
        return self._value
