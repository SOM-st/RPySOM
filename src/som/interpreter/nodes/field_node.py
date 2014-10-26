from .expression_node import ExpressionNode

from som.vmobjects.abstract_object import AbstractObject
from som.vmobjects.object          import Object


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
        return self.do_read(self_obj)


def _make_field_read_node_class(field_idx):
    class _FieldReadNodeI(FieldReadNode):
        def do_read(self, self_obj):
            return getattr(self_obj, "_field" + str(field_idx))
    return _FieldReadNodeI


def _make_field_read_node_classes(count):
    return [_make_field_read_node_class(i + 1) for i in range(count)]


class FieldReadNodeN(FieldReadNode):
    
    _immutable_fields_ = ["_extension_index"]
    
    def __init__(self, self_exp, extension_index, source_section = None):
        FieldReadNode.__init__(self, self_exp, source_section)
        assert extension_index >= 0
        self._extension_index = extension_index

    def do_read(self, self_obj):
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
        assert isinstance(value, AbstractObject)
        self.do_write(self_obj, value)
        return value


def _make_field_write_node_class(field_idx):
    class _FieldWriteNodeI(FieldWriteNode):
        def do_write(self, self_obj, value):
            setattr(self_obj, "_field" + str(field_idx), value)
    return _FieldWriteNodeI


def _make_field_write_node_classes(count):
    return [_make_field_write_node_class(i + 1) for i in range(count)]


class FieldWriteNodeN(FieldWriteNode):
    
    _immutable_fields_ = ["_extension_index"]
    
    def __init__(self, self_exp, value_exp, extension_index, source_section = None):
        FieldWriteNode.__init__(self, self_exp, value_exp, source_section)
        assert extension_index >= 0
        self._extension_index = extension_index

    def do_write(self, self_obj, value):
        self_obj._fields[self._extension_index] = value


_field_read_node_classes  = _make_field_read_node_classes(Object.NUMBER_OF_DIRECT_FIELDS)
_field_write_node_classes = _make_field_write_node_classes(Object.NUMBER_OF_DIRECT_FIELDS)


def create_read_node(self_exp, index):
    if index < Object.NUMBER_OF_DIRECT_FIELDS:
        return _field_read_node_classes[index](self_exp)
    else:
        return FieldReadNodeN(self_exp, index - Object.NUMBER_OF_DIRECT_FIELDS)


def create_write_node(self_exp, index, value_exp):
    if index < Object.NUMBER_OF_DIRECT_FIELDS:
        return _field_write_node_classes[index](self_exp, value_exp)
    else:
        return FieldWriteNodeN(self_exp, value_exp, index - Object.NUMBER_OF_DIRECT_FIELDS)

