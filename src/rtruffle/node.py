from rpython.rlib.unroll import unrolling_iterable
from rtruffle.source_section import SourceSection


class AbstractNode(object):
    pass


def _get_all_child_fields(cls):
    field_names = []
    while cls is not AbstractNode:
        if hasattr(cls, '_child_nodes_'):
            field_names = field_names + cls._child_nodes_
        cls = cls.__base__
    return field_names


def _generate_replace_method(cls):
    child_fields = unrolling_iterable(_get_all_child_fields(cls))

    def _replace_child_with(parent_node, old_child, new_child):
        was_replaced = False
        for child_slot in child_fields:
            if child_slot.endswith('[*]'):
                slot_name = child_slot[:-3]
                nodes = getattr(parent_node, slot_name)
                if nodes and old_child in nodes:
                    # update old list, because iterators might have a copy of it
                    for i, n in enumerate(nodes):
                        if n is old_child:
                            nodes[i] = new_child
                    setattr(parent_node, slot_name, nodes[:])  # TODO: figure out whether we need the copy of the list here
                    was_replaced = True
            else:
                current = getattr(parent_node, child_slot)
                if current is old_child:
                    setattr(parent_node, child_slot, new_child)
                    was_replaced = True
        # TODO: method recursion is a problem causing specialization more than
        #       once of a node if the containing method is already on the stack
        # if not was_replaced:
        #     raise ValueError("%s was not a direct child node of %s" % (
        #         old_child, parent_node))
        return new_child

    cls._replace_child_with = _replace_child_with


class NodeInitializeMetaClass(type):
    def __init__(cls, name, bases, dic):
        type.__init__(cls, name, bases, dic)
        cls._initialize_node_class()

    def _initialize_node_class(cls):
        _generate_replace_method(cls)


class Node(AbstractNode):
    __metaclass__ = NodeInitializeMetaClass

    _immutable_fields_ = ['_source_section', '_parent']
    _child_nodes_      = []

    def __init__(self, source_section = None):
        assert (source_section is None or
                isinstance(source_section, SourceSection))
        self._source_section = source_section
        self._parent         = None

    def get_parent(self):
        return self._parent

    def assign_source_section(self, source_section):
        assert isinstance(source_section, SourceSection)
        if self._source_section:
            raise ValueError("Source section already set.")
        self._source_section = source_section

    def get_source_section(self):
        return self._source_section

    def adopt_child(self, node):
        assert isinstance(node, Node) or node is None
        if node:
            node._parent = self
        return node

    def adopt_children(self, nodes):
        if nodes is None:
            return None

        children = nodes[:]  # we return here a copy to make it clear to RPython
                             # that the list is not resized, and,
                             # the quasi-immutable support does not work on
                             # element-level, so, we will need to copy the lists
                             # when replacing child nodes

        for child in children:
            child._parent = self
        return children

    def replace(self, node):
        if node:
            self._parent._replace_child_with(self, node)
            node._parent = self._parent
            return node
        else:
            return None

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self._source_section)
