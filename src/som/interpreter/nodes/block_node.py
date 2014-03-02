from .literal_node import LiteralNode
from rtruffle.node import initialize_node_class


class BlockNode(LiteralNode):

    _immutable_fields_ = ['_universe']

    def __init__(self, value, universe, source_section = None):
        LiteralNode.__init__(self, value, source_section)
        self._universe = universe

    def execute(self, frame):
        return self._universe.new_block(self._value, None)


class BlockNodeWithContext(BlockNode):

    def __init__(self, value, universe, source_section = None):
        BlockNode.__init__(self, value, universe, source_section)

    def execute(self, frame):
        return self._universe.new_block(self._value, frame)


initialize_node_class(BlockNode)
initialize_node_class(BlockNodeWithContext)
