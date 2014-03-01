from ..interpreter.nodes.nonlocal_variable_read_node import (
    NonLocalVariableReadNode, NonLocalVariableWriteNode, NonLocalSuperReadNode,
    NonLocalSelfReadNode)


class Variable(object):

    def __init__(self, name, frame_idx):
        self._name      = name
        self._frame_idx = frame_idx
        self._is_read   = False
        self._is_read_out_of_context = False

    def get_frame_idx(self):
        return self._frame_idx

    def is_accessed(self):
        return self._is_read

    def is_accessed_out_of_context(self):
        return  self._is_read_out_of_context

    def get_read_node(self, context_level):
        self._is_read = True
        if context_level > 0:
            self._is_read_out_of_context = True
        # TODO: for later versions with specialization support
        #return UninitializedVariableReadNode(self, context_level)

    def get_super_read_node(self, context_level, holder_class_name,
                            on_class_side, universe):
        self._is_read = True
        if context_level > 0:
            self._is_read_out_of_context = True
        return NonLocalSuperReadNode(context_level, holder_class_name,
                                     on_class_side, universe)
        # TODO: for later versions with specialization support
        # return UninitializedSuperReadNode(self, context_level,
        #                                   holder_class_name, on_class_side)


class Argument(Variable):

    def __init__(self, name, frame_idx):
        Variable.__init__(self, name, frame_idx)

    def get_read_node(self, context_level):
        Variable.get_read_node(self, context_level)
        if self._name == "self":
            return NonLocalSelfReadNode(context_level, None)
        return NonLocalVariableReadNode(context_level, self._frame_idx, True)


class Local(Variable):

    def __init__(self, name, frame_idx):
        Variable.__init__(self, name, frame_idx)
        self._is_written = False
        self._is_written_out_of_context = False

    def is_accessed(self):
        return Variable.is_accessed() or self._is_written

    def is_accessed_out_of_context(self):
        return (Variable.is_accessed_out_of_context(self) or
                self._is_written_out_of_context)

    def get_read_node(self, context_level):
        Variable.get_read_node(self, context_level)
        return NonLocalVariableReadNode(context_level, self._frame_idx, False)

    def get_write_node(self, context_level, value_expr):
        self._is_written = True
        if context_level > 0:
            self._is_written_out_of_context = True
        # TODO: for later versions with specialization support
        return NonLocalVariableWriteNode(context_level, self._frame_idx,
                                         value_expr)
        return UninitializedVariableWriteNode(self, context_level, value_expr)
