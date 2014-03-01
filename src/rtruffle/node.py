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
        return nodes
