class Node(object):

    _immutable_fields_ = ['_source_section', '_parent']
    _child_nodes_      = []

    def __init__(self, source_section = None):
        self._source_section = source_section
        self._parent         = None

    def get_parent(self):
        return self._parent

    def assign_source_section(self, source_section):
        if self._source_section:
            raise ValueError("Source section already set.")
        self._source_section = source_section

    def get_source_section(self):
        return self._source_section

    def adopt_child(self, node):
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
            was_replaced = False
            for child_slot in self._parent._child_nodes_:
                if child_slot.endswith('[*]'):
                    slot_name = child_slot[:-3]
                    nodes = getattr(self._parent, slot_name)
                    if self in nodes:
                        new_children = [node if n is self else n
                                        for n in nodes]
                        setattr(self._parent, slot_name, new_children)
                        was_replaced = True
                else:
                    current = getattr(self._parent, child_slot)
                    if current is self:
                        setattr(self._parent, child_slot, node)
                        was_replaced = True
            if not was_replaced:
                raise ValueError("%s was not a direct child node of %s" % (
                    self, self._parent))
        return node

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self._source_section)
