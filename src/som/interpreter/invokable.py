from rpython.rlib import jit
from rtruffle.node import Node

from .frame import Frame

def get_printable_location(invokable):
    return invokable._source_section._identifier

jitdriver = jit.JitDriver(
     greens=['self'],
     reds= ['arguments', 'caller_frame', 'receiver'],
     # virtualizables=['caller_frame'])
      get_printable_location=get_printable_location,

     # the next line is a workaround around a likely bug in RPython
     # for some reason, the inlining heuristics default to "never inline" when
     # two different jit drivers are involved (in our case, the primitive
     # driver, and this one).

     # the next line says that calls involving this jitdriver should always be
     # inlined once (which means that things like Integer>>< will be inlined
     # into a while loop again, when enabling this driver).
     should_unroll_one_iteration = lambda self: True)


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
        jitdriver.jit_merge_point(self      = self,
                                  receiver  = receiver,
                                  arguments = arguments,
                                  caller_frame = caller_frame)

        frame = Frame(receiver, arguments, self._number_of_temps,
                      caller_frame, self._universe.nilObject)
        return self._expr_or_sequence.execute(frame)
