from rpython.rlib import rerased
from rpython.rlib.jit import promote, JitDriver
from rpython.rlib.objectmodel import instantiate
from .abstract_object import AbstractObject
from rpython.rlib.debug import make_sure_not_resized
from som.vm.globals import nilObject
from som.vmobjects.double import Double
from som.vmobjects.integer import Integer
from som.vmobjects.method import Method


class _ArrayStrategy(object):
    pass


def put_all_obj_pl(block_method):
    assert isinstance(block_method, Method)
    return "#putAll: (obj_strategy) %s" % block_method.merge_point_string()

put_all_obj_driver = JitDriver(greens=['block_method'], reds='auto',
                               get_printable_location=put_all_obj_pl)


class _ObjectStrategy(_ArrayStrategy):

    _erase, _unerase = rerased.new_erasing_pair("list")
    _erase   = staticmethod(_erase)
    _unerase = staticmethod(_unerase)

    def get_idx(self, storage, idx):
        store = self._unerase(storage)
        return store[idx]

    def set_idx(self, array, idx, value):
        assert isinstance(array, Array)
        store = self._unerase(array._storage)
        store[idx] = value

    def set_all(self, array, value):
        assert isinstance(array, Array)
        assert isinstance(value, AbstractObject)

        store = self._unerase(array._storage)
        assert isinstance(store, list)

        for i, _ in enumerate(store):
            store[i] = value

    def set_all_with_block(self, array, block):
        assert isinstance(array, Array)
        block_method = block.get_method()
        store = self._unerase(array._storage)

        i = 0
        length = len(store)

        # we do the first iteration separately to determine our strategy
        if i < length:
            first = block_method.invoke(block, [])
            # TODO: determine strategy
            store[0] = first
            i += 1

        while i < length:
            put_all_obj_driver.jit_merge_point(block_method = block_method)
            store[i] = block_method.invoke(block, [])
            i += 1

    def as_arguments_array(self, storage):
        return self._unerase(storage)

    def get_size(self, storage):
        return len(self._unerase(storage))

    @staticmethod
    def new_storage_for(size):
        return _ObjectStrategy._erase([nilObject] * size)

    @staticmethod
    def new_storage_with_values(values):
        assert isinstance(values, list)
        make_sure_not_resized(values)
        return _ObjectStrategy._erase(values)

    def copy(self, storage):
        store = self._unerase(storage)
        return Array._from_storage_and_strategy(self._erase(store[:]), _obj_strategy)

    def copy_and_extend_with(self, storage, value):
        store = self._unerase(storage)
        old_size = len(store)
        new_size = old_size + 1

        new = [None] * new_size

        for i, _ in enumerate(store):
            new[i] = store[i]

        new[old_size]  = value

        return Array._from_storage_and_strategy(self._erase(new), _obj_strategy)


# class _LongStrategy(_ArrayStrategy):
#
#     @staticmethod
#     def get_idx(storage, idx):
#         pass
#
#
# class _DoubleStrategy(object):
#     pass
#

class _EmptyStrategy(_ArrayStrategy):

    # We have these basic erase/unerase methods, and then the once to be used, which
    # do also the wrapping with Integer objects of the integer value
    __erase, __unerase = rerased.new_erasing_pair("Integer")
    __erase   = staticmethod(__erase)
    __unerase = staticmethod(__unerase)

    def _erase(self, anInt):
        assert isinstance(anInt, int)
        return self.__erase(Integer(anInt))

    def _unerase(self, storage):
        return self.__unerase(storage).get_embedded_integer()

    def get_idx(self, storage, idx):
        size = self._unerase(storage)
        if 0 <= idx < size:
            return nilObject
        else:
            raise IndexError()

    def set_idx(self, array, idx, value):
        size = self._unerase(array._storage)
        if 0 <= idx < size:
            assert isinstance(value, AbstractObject)
            #if isinstance(value, Integer):
            #TODO: logic to transition to _PartiallyEmpty or so...
            new = [nilObject] * size
            new[idx] = value
            array._storage  = _obj_strategy._erase(new)
            array._strategy = _obj_strategy
        else:
            raise IndexError()

    def set_all(self, array, value):
        # todo: add support for other strategies
        size = self._unerase(array._storage)
        if size > 0:
            new = [value] * size
            array._storage  = _obj_strategy._erase(new)
            array._strategy = _obj_strategy

    def set_all_with_block(self, array, block):
        size = self._unerase(array._storage)
        # TODO: do something smarter...
        array._storage  = _obj_strategy._erase([None] * size)
        array._strategy = _obj_strategy
        _obj_strategy.set_all_with_block(array, block)

    def as_arguments_array(self, storage):
        size = self._unerase(storage)
        return [nilObject] * size

    def get_size(self, storage):
        size = self._unerase(storage)
        return size

    @staticmethod
    def new_storage_for(size):
        return _empty_strategy._erase(size)

    @staticmethod
    def new_storage_with_values(values):
        return _empty_strategy._erase(len(values))

    def copy(self, storage):
        return Array._from_storage_and_strategy(storage, _empty_strategy)

    def copy_and_extend_with(self, storage, value):
        size = self._unerase(storage)
        if value is nilObject:
            return Array.from_size(size + 1)
        else:
            new = [nilObject] * (size + 1)
            new[-1] = value
            return Array._from_storage_and_strategy(_ObjectStrategy._erase(new),
                                                   _obj_strategy)


# class _PartiallyEmpty(_ArrayStrategy):
#     # This is an array that is slowly filled, we have the hope that it will
#     # turn out to be homogeneous
#
#     # it uses a boxed representation, but keeps also track of the type of all
#     # non-nil elements
#     pass

_obj_strategy    = _ObjectStrategy()
# _long_strategy   = _LongStrategy()
# _double_strategy = _DoubleStrategy()
_empty_strategy  = _EmptyStrategy()


class Array(AbstractObject):

    # _strategy is the strategy object
    # _storage depends on the strategy, can be for instance a typed list,
    # or for the empty strategy the size as an Integer object,
    # or something more complex

    @staticmethod
    def _from_storage_and_strategy(storage, strategy):
        self = instantiate(Array)
        # self = Array()
        self._strategy = strategy
        self._storage  = storage
        return self

    @staticmethod
    def from_size(size, strategy = _empty_strategy):
        self = instantiate(Array)
        # self = Array()
        self._strategy = strategy
        self._storage  = strategy.new_storage_for(size)
        return self

    @staticmethod
    def from_values(values, strategy = None):
        self = instantiate(Array)
        # self = Array()
        if strategy is None:
            self._strategy = self._determine_strategy(values)
        else:
            self._strategy = strategy
        self._storage = self._strategy.new_storage_with_values(values)
        return self

    @staticmethod
    def from_objects(values):
        return Array.from_values(values, _obj_strategy)

    @staticmethod
    def _determine_strategy(values):
        is_empty    = True
        only_double = True
        only_long   = True
        for v in values:
            if v is None or v is nilObject:
                continue
            if isinstance(v, int) or isinstance(v, Integer):
                only_double = False
                is_empty    = False
                continue
            if isinstance(v, float) or isinstance(v, Double):
                only_long = False
                is_empty  = False
                continue
            only_long   = False
            only_double = False
            is_empty    = False

        if is_empty:
            return _empty_strategy
        # if only_double:
        #     return _double_strategy
        # if only_long:
        #     return _long_strategy
        return _obj_strategy

    def get_indexable_field(self, index):
        # Get the indexable field with the given index
        return self._strategy.get_idx(self._storage, index)

    def set_indexable_field(self, index, value):
        # Set the indexable field with the given index to the given value
        self._strategy.set_idx(self, index, value)

    def set_all(self, value):
        self._strategy.set_all(self, value)

    def set_all_with_block(self, block):
        self._strategy.set_all_with_block(self, block)

    def as_argument_array(self):
        return self._strategy.as_arguments_array(self._storage)

    def get_number_of_indexable_fields(self):
        # Get the number of indexable fields in this array
        return self._strategy.get_size(self._storage)

    def copy(self):
        return self._strategy.copy(self._storage)

    def copy_and_extend_with(self, value):
        return self._strategy.copy_and_extend_with(self._storage, value)

    def get_class(self, universe):
        return universe.arrayClass
