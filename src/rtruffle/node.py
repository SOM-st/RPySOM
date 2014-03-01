class Node(object):

    _immutable_fields_ = ['_source_section']

    def __init__(self, source_section = None):
        self._source_section = source_section

    def assign_source_section(self, source_section):
        if self._source_section:
            raise ValueError("Source section already set.")
        self._source_section = source_section

    def get_source_section(self):
        return self._source_section

    def adopt_child(self, node):
        #TODO: print "NOT YET IMPLEMENTED: adopt_child"
        return node

    def adopt_children(self, nodes):
        #TODO: print "NOT YET IMPLEMENTED: adopt_children"
        if nodes is None:
            return None
        return nodes[:]  # we return here a copy to make it clear to RPython
                         # that the list is not resized, and,
                         # the quasi-immutable support does not work on
                         # element-level, so, we will need to copy the lists
                         # when replacing child nodes

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self._source_section)
