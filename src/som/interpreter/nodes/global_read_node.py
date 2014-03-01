from .expression_node import ExpressionNode


class GenericGlobalReadNode(ExpressionNode):

    _immutable_fields_ = ["_global_name", "_universe"]

    def __init__(self, global_name, universe, source_section = None):
        ExpressionNode.__init__(self, source_section)
        self._global_name = global_name
        self._universe    = universe

    def execute(self, frame):
        if self._universe.has_global(self._global_name):
            assoc = self._universe.get_globals_association(self._global_name)
            return assoc.get_value()
        else:
            return frame.get_self().send_unknown_global(frame,
                                                        self._global_name,
                                                        self._universe)
