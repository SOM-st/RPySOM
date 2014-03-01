from rtruffle.node import Node


class FieldNode(Node):

    _immutable_fields_ = ["_self_exp?", "_field_idx"]
    _child_nodes_      = ["_self_exp"]

    def __init__(self, self_exp, field_idx):
        Node.__init__(self)
        self._self_exp  = self.adopt_child(self_exp)
        self._field_idx = field_idx


class FieldReadNode(FieldNode):

    def __init__(self, self_exp, field_idx):
        FieldNode.__init__(self, self_exp, field_idx)

    def execute(self, frame):
        self_obj = self._self_exp.execute(frame)
        return self_obj.get_field(self._field_idx)


class FieldWriteNode(FieldNode):

    _immutable_fields_ = ["_value_exp?"]
    _child_nodes_      = ["_value_exp"]

    def __init__(self, self_exp, field_idx, value_exp):
        FieldNode.__init__(self, self_exp, field_idx)
        self._value_exp = self.adopt_child(value_exp)

    def execute(self, frame):
        self_obj = self._self_exp.execute(frame)
        value    = self._value_exp.execute(frame)
        self_obj.set_field(self._field_idx, value)
        return value
