from rpython.rlib import jit
from som.vmobjects.block_ast import AstBlock
from som.vmobjects.method_ast import AstMethod
from som.vmobjects.primitive   import Primitive
from som.primitives.primitives import Primitives


def _at(ivkbl, rcvr, args):
    i    = args[0]
    return  rcvr.get_indexable_field(i.get_embedded_integer() - 1)


def _at_put(ivkbl, rcvr, args):
    value = args[1]
    index = args[0]

    rcvr.set_indexable_field(index.get_embedded_integer() - 1, value)
    return value


def _length(ivkbl, rcvr, args):
    return ivkbl.get_universe().new_integer(
        rcvr.get_number_of_indexable_fields())


def _new(ivkbl, rcvr, args):
    length = args[0]

    return ivkbl.get_universe().new_array_with_length(
        length.get_embedded_integer())


def get_do_index_printable_location(block_method):
    assert isinstance(block_method, AstMethod)
    return "#doIndexes: %s" % block_method.merge_point_string()


do_index_driver = jit.JitDriver(
    greens=['block_method'], reds='auto',
    is_recursive=True,
    get_printable_location=get_do_index_printable_location)


def _do_indexes(ivkbl, rcvr, args):
    block = args[0]
    block_method = block.get_method()
    universe = ivkbl.get_universe()

    i = 1
    length = rcvr.get_number_of_indexable_fields()
    while i <= length:  # the i is propagated to Smalltalk, so, start with 1
        do_index_driver.jit_merge_point(block_method = block_method)
        block_method.invoke(block, [universe.new_integer(i)])
        i += 1


def get_do_printable_location(block_method):
    assert isinstance(block_method, AstMethod)
    return "#doIndexes: %s" % block_method.merge_point_string()


do_driver = jit.JitDriver(greens=['block_method'], reds='auto',
                          get_printable_location=get_do_printable_location)


def _do(ivkbl, rcvr, args):
    block = args[0]
    block_method = block.get_method()

    i = 0
    length = rcvr.get_number_of_indexable_fields()
    while i < length:  # the array itself is zero indexed
        do_driver.jit_merge_point(block_method = block_method)
        block_method.invoke(block, [rcvr.get_indexable_field(i)])
        i += 1


def _copy(ivkbl, rcvr, args):
    return rcvr.copy()


def _put_all(ivkbl, rcvr, args):
    arg = args[0]
    if isinstance(arg, AstBlock):
        rcvr.set_all_with_block(arg)
        return rcvr

    # It is a simple value, just put it into the array

    # TODO: move to array, and adapt to use strategies
    rcvr.set_all(arg)
    return rcvr


class ArrayPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("at:",     self._universe, _at))
        self._install_instance_primitive(Primitive("at:put:", self._universe, _at_put))
        self._install_instance_primitive(Primitive("length",  self._universe, _length))
        self._install_instance_primitive(Primitive("copy",    self._universe, _copy))

        self._install_instance_primitive(Primitive("doIndexes:", self._universe, _do_indexes))
        self._install_instance_primitive(Primitive("do:",        self._universe, _do))
        self._install_instance_primitive(Primitive("putAll:",    self._universe, _put_all))

        self._install_class_primitive(Primitive("new:",       self._universe, _new))
