from rtruffle.node import Node, initialize_node_class

from .frame import Frame


class Invokable(Node):

    _immutable_fields_ = ['_expr_or_sequence?', '_universe', '_number_of_temps']
    _child_nodes_      = ['_expr_or_sequence']

    def __init__(self, source_section, expr_or_sequence, number_of_temps,
                 universe):
        Node.__init__(self, source_section)
        self._expr_or_sequence = self.adopt_child(expr_or_sequence)
        self._universe         = universe
        self._number_of_temps  = number_of_temps

    def invoke(self, caller_frame, receiver, arguments):
        frame = Frame(receiver, arguments, self._number_of_temps,
                      caller_frame, self._universe.nilObject)
        return self._expr_or_sequence.execute(frame)


initialize_node_class(Invokable)
