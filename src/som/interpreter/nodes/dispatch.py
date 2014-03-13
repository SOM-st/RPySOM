from rtruffle.node import Node

_INLINE_CACHE_SIZE = 6


class _AbstractDispatchNode(Node):

    def __init__(self):
        Node.__init__(self, source_section = None)


class _AbstractDispatchWithLookup(_AbstractDispatchNode):

    _immutable_fields_ = ['_selector', '_universe']

    def __init__(self, selector, universe):
        self._selector = selector
        self._universe = universe


class UninitializedDispatchNode(_AbstractDispatchWithLookup):

    def _chain_depth_and_first_dispatch_node(self):
        node = self
        chain_depth = 0
        while isinstance(node.get_parent(), _AbstractDispatchNode):
            node = node.get_parent()
            chain_depth += 1
        return chain_depth, node

    def dispatch(self, frame, rcvr, args):
        chain_depth, first_node = self._chain_depth_and_first_dispatch_node()

        if chain_depth < _INLINE_CACHE_SIZE:
            rcvr_class = rcvr.get_class(self._universe)
            method = rcvr_class.lookup_invokable(self._selector)

            new_chain_end = UninitializedDispatchNode(self._selector,
                                                      self._universe)
            caching_node = CachedDispatchNode(method, rcvr_class, new_chain_end,
                                              self._universe)
            return self.replace(caching_node).dispatch(frame, rcvr, args)
        else:
            ## Cache is to long, call site is megamorphic
            generic_node = GenericDispatchNode(self._selector, self._universe)
            first_node.get_parent().replace_dispatch_chain(generic_node)
            return generic_node.dispatch(frame, rcvr, args)


class _AbstractCachingDispatchNode(_AbstractDispatchNode):

    _immutable_fields_ = ['_method']

    def __init__(self, method):
        _AbstractDispatchNode.__init__(self)
        self._cached_method = method


class CachedDispatchNode(_AbstractCachingDispatchNode):

    _immutable_fields_ = ['_rcvr_class', '_next_in_cache?', '_universe']
    _child_nodes_      = ['_next_in_cache']

    def __init__(self, method, rcvr_class, next_in_cache, universe):
        _AbstractCachingDispatchNode.__init__(self, method)
        self._next_in_cache = self.adopt_child(next_in_cache)
        self._rcvr_class    = rcvr_class
        self._universe      = universe

    def dispatch(self, frame, rcvr, args):
        if self._rcvr_class is rcvr.get_class(self._universe):
            return self._cached_method.invoke(frame, rcvr, args)
        else:
            return self._next_in_cache.dispatch(frame, rcvr, args)


class SuperDispatchNode(_AbstractCachingDispatchNode):

    def __init__(self, selector, super_node):
        method = super_node.get_super_class().lookup_invokable(selector)
        assert method is not None  # DNU with super sent is not yet implemented.
        _AbstractCachingDispatchNode.__init__(self, method)

    def dispatch(self, frame, rcvr, args):
        return self._cached_method.invoke(frame, rcvr, args)


class GenericDispatchNode(_AbstractDispatchWithLookup):

    def _lookup(self, rcvr):
        rcvr_class = rcvr.get_class(self._universe)
        return rcvr_class.lookup_invokable(self._selector)

    def dispatch(self, frame, rcvr, args):
        method = self._lookup(rcvr)
        if method is not None:
            return method.invoke(frame, rcvr, args)
        else:
            return rcvr.send_does_not_understand(frame, self._selector, args,
                                                 self._universe)
