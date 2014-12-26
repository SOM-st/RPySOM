from rpython.rlib.jit import we_are_jitted
from rtruffle.node import Node
from som.interpreter.objectstorage.storage_location import \
    UninitializedStorageLocationException, GeneralizeStorageLocationException
from som.vmobjects.object import Object


def create_read(nilObject, field_idx):
    return _UninitializedReadFieldNode(nilObject, field_idx)


def create_write(nilObject, field_idx):
    return _UninitializedWriteFieldNode(nilObject, field_idx)


class _AbstractFieldAccessorNode(Node):
    _immutable_fields_ = ['_field_idx', '_nilObject']

    def __init__(self, nilObject, field_idx):
        Node.__init__(self)
        self._field_idx = field_idx
        self._nilObject = nilObject


class _AbstractReadFieldNode(_AbstractFieldAccessorNode):

    def _specialize_and_read(self, obj, reason, next_read_node):
        return self._specialize(obj, reason, next_read_node).read(obj)

    def _specialize(self, obj, reason, next_read_node):
        assert isinstance(obj, Object)
        obj.update_layout_to_match_class(self._nilObject)

        layout = obj.get_object_layout()
        location = layout.get_storage_location(self._field_idx)

        node = _SpecializedReadFieldNode(self._nilObject, self._field_idx,
                                         layout, location, next_read_node)
        return self.replace(node)


class _UninitializedReadFieldNode(_AbstractReadFieldNode):

    def read(self, obj):
        if we_are_jitted():
            assert False
        return self._specialize_and_read(obj, "uninitialized node",
                                         _UninitializedReadFieldNode(
                                             self._nilObject, self._field_idx))


class _SpecializedReadFieldNode(_AbstractReadFieldNode):
    _immutable_fields_ = ['_layout', '_next?', '_location']
    _child_nodes_      = ['_next']

    def __init__(self, nilObject, field_idx, layout, location, next_read_node):
        _AbstractReadFieldNode.__init__(self, nilObject, field_idx)
        self._layout   = layout
        self._location = location
        self._next = self.adopt_child(next_read_node)

    def read(self, obj):
        if self._layout is obj.get_object_layout():
            return self._location.read_location(obj)
        else:
            return self._respecialize_or_next(obj).read(obj)

    def _respecialize_or_next(self, obj):
        if self._layout.is_for_same_class(obj.get_class(None)):
            return self._specialize(obj, "update outdated node", self._next)
        else:
            return self._next


class _AbstractWriteFieldNode(_AbstractFieldAccessorNode):

    def _write_and_respecialize(self, obj, value, reason, next_write_node):
        obj.set_field(self._field_idx, value, self._nilObject)
        return self._respecialize(obj, value, next_write_node)

    def _respecialize(self, obj, value, next_write_node):
        layout = obj.get_object_layout()
        location = layout.get_storage_location(self._field_idx)
        node = _SpecializedWriteFieldNode(self._nilObject, self._field_idx,
                                          layout, location, next_write_node)
        return self.replace(node)


class _UninitializedWriteFieldNode(_AbstractWriteFieldNode):

    def write(self, obj, value):
        self._write_and_respecialize(obj, value, "initialize write node",
                                     _UninitializedWriteFieldNode(
                                         self._nilObject, self._field_idx))
        return value


class _SpecializedWriteFieldNode(_AbstractWriteFieldNode):
    _immutable_fields_ = ['_layout', '_next?', '_location']
    _child_nodes_      = ['_next']

    def __init__(self, nilObject, field_idx, layout, location, next_write_node):
        _AbstractWriteFieldNode.__init__(self, nilObject, field_idx)
        self._layout = layout
        self._location = location
        self._next = self.adopt_child(next_write_node)

    def _do_write(self, obj, value):
        try:
            self._location.write_location(obj, value)
            return
        except UninitializedStorageLocationException:
            obj._update_layout_with_initialized_field(self._nilObject,
                                                       self._field_idx,
                                                       value.__class__)
        except GeneralizeStorageLocationException:
            obj._update_layout_with_generalized_field(self._nilObject,
                                                       self._field_idx)
        self._respecialize(obj, value, self._next).write(obj, value)

    def write(self, obj, value):
        if self._layout is obj.get_object_layout():
            self._do_write(obj, value)
        else:
            if self._layout.is_for_same_class(obj.get_class(None)):
                self._write_and_respecialize(obj, value, "update outdated node",
                                             self._next)
            else:
                self._next.write(obj, value)
