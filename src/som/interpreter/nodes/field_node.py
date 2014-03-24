from .expression_node import ExpressionNode
from som.vmobjects.object import Object


def create_read_node(self_exp, index):
    if index == 0: return FieldReadNode1(self_exp)
    if index == 1: return FieldReadNode2(self_exp)
    if index == 2: return FieldReadNode3(self_exp)
    if index == 3: return FieldReadNode4(self_exp)
    if index == 4: return FieldReadNode5(self_exp)
    return FieldReadNodeN(self_exp, Object.NUMBER_OF_DIRECT_FIELDS - index)
    

def create_write_node(self_exp, index, value_exp):
    if index == 0: return FieldWriteNode1(self_exp, value_exp)
    if index == 1: return FieldWriteNode2(self_exp, value_exp)
    if index == 2: return FieldWriteNode3(self_exp, value_exp)
    if index == 3: return FieldWriteNode4(self_exp, value_exp)
    if index == 4: return FieldWriteNode5(self_exp, value_exp)
    return FieldWriteNodeN(self_exp, value_exp, Object.NUMBER_OF_DIRECT_FIELDS - index)


class FieldNode(ExpressionNode):

    _immutable_fields_ = ["_self_exp?"]
    _child_nodes_      = ["_self_exp"]

    def __init__(self, self_exp, source_section = None):
        ExpressionNode.__init__(self, source_section)
        self._self_exp  = self.adopt_child(self_exp)


class FieldReadNode(FieldNode):

    def execute(self, frame):
        self_obj = self._self_exp.execute(frame)
        assert isinstance(self_obj, Object)
        return self.read(self_obj)


class FieldReadNode1(FieldReadNode):

    def read(self, self_obj):
        return self_obj._field1


class FieldReadNode2(FieldReadNode):

    def read(self, self_obj):
        return self_obj._field2


class FieldReadNode3(FieldReadNode):

    def read(self, self_obj):
        return self_obj._field3


class FieldReadNode4(FieldReadNode):

    def read(self, self_obj):
        return self_obj._field4


class FieldReadNode5(FieldReadNode):

    def read(self, self_obj):
        return self_obj._field5


class FieldReadNodeN(FieldReadNode):
    
    _immutable_fields_ = ["_extension_index"]
    
    def __init__(self, self_exp, extension_index, source_section = None):
        FieldReadNode.__init__(self, self_exp, source_section)
        self._extension_index = extension_index

    def read(self, self_obj):
        return self_obj._fields[self._extension_index]


class FieldWriteNode(FieldNode):

    _immutable_fields_ = ["_value_exp?"]
    _child_nodes_      = ["_value_exp"]

    def __init__(self, self_exp, value_exp, source_section = None):
        FieldNode.__init__(self, self_exp, source_section)
        self._value_exp = self.adopt_child(value_exp)

    def execute(self, frame):
        self_obj = self._self_exp.execute(frame)
        value    = self._value_exp.execute(frame)
        assert isinstance(self_obj, Object)
        self.write(self_obj, value)
        return value


class FieldWriteNode1(FieldWriteNode):
    
    def write(self, self_obj, value):
        self_obj._field1 = value


class FieldWriteNode2(FieldWriteNode):
    
    def write(self, self_obj, value):
        self_obj._field2 = value


class FieldWriteNode3(FieldWriteNode):
    
    def write(self, self_obj, value):
        self_obj._field3 = value


class FieldWriteNode4(FieldWriteNode):
    
    def write(self, self_obj, value):
        self_obj._field4 = value


class FieldWriteNode5(FieldWriteNode):
    
    def write(self, self_obj, value):
        self_obj._field5 = value


class FieldWriteNodeN(FieldWriteNode):
    
    _immutable_fields_ = ["_extension_index"]
    
    def __init__(self, self_exp, value_exp, extension_index, source_section = None):
        FieldWriteNode.__init__(self, self_exp, value_exp, source_section)
        self._extension_index = extension_index

    def write(self, self_obj, value):
        self_obj._fields[self._extension_index] = value
