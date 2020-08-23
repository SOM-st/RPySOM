from rpython.rlib.rarithmetic import ovfcheck
from rpython.rlib.rbigint import rbigint
from som.vmobjects.abstract_object import AbstractObject
from som.vmobjects.biginteger import BigInteger
from som.vmobjects.double import Double


class Integer(AbstractObject):

    _immutable_fields_ = ["_embedded_integer"]

    def __init__(self, value):
        AbstractObject.__init__(self)
        assert isinstance(value, int)
        self._embedded_integer = value

    def get_embedded_integer(self):
        return self._embedded_integer

    def __str__(self):
        return str(self._embedded_integer)

    def get_class(self, universe):
        return universe.integerClass

    def quick_add(self, from_method, frame, interpreter, bytecode_index):
        right = frame.get_stack_element(0)
        frame.pop()
        frame.pop()
        frame.push(self.prim_add(right, interpreter.get_universe()))

    def quick_multiply(self, from_method, frame, interpreter, bytecode_index):
        right = frame.get_stack_element(0)
        frame.pop()
        frame.pop()
        frame.push(self.prim_multiply(right, interpreter.get_universe()))

    def quick_subtract(self, from_method, frame, interpreter, bytecode_index):
        right = frame.get_stack_element(0)
        frame.pop()
        frame.pop()
        frame.push(self.prim_subtract(right, interpreter.get_universe()))

    def _to_double(self, universe):
        return universe.new_double(float(self._embedded_integer))

    def prim_less_than(self, right, universe):
        # Check second parameter type:
        if isinstance(right, BigInteger):
            result = rbigint.fromint(self._embedded_integer).lt(
                right.get_embedded_biginteger())
        elif isinstance(right, Double):
            return self._to_double(universe).prim_less_than(right, universe)
        else:
            result = self._embedded_integer < right.get_embedded_integer()

        if result:
            return universe.trueObject
        else:
            return universe.falseObject

    def prim_as_string(self, universe):
        return universe.new_string(str(self._embedded_integer))

    def prim_add(self, right, universe):
        if isinstance(right, BigInteger):
            return universe.new_biginteger(
                right.get_embedded_biginteger().add(
                    rbigint.fromint(self._embedded_integer)))
        elif isinstance(right, Double):
            return self._to_double(universe).prim_add(right, universe)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            try:
                result = ovfcheck(l + r)
                return universe.new_integer(result)
            except OverflowError:
                return universe.new_biginteger(
                    rbigint.fromint(l).add(rbigint.fromint(r)))

    def prim_subtract(self, right, universe):
        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).sub(
                right.get_embedded_biginteger())
            return universe.new_biginteger(r)
        elif isinstance(right, Double):
            return self._to_double(universe).prim_subtract(right, universe)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            try:
                result = ovfcheck(l - r)
                return universe.new_integer(result)
            except OverflowError:
                return universe.new_biginteger(
                    rbigint.fromint(l).sub(rbigint.fromint(r)))

    def prim_multiply(self, right, universe):
        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).mul(
                right.get_embedded_biginteger())
            return universe.new_biginteger(r)
        elif isinstance(right, Double):
            return self._to_double(universe).prim_multiply(right, universe)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            try:
                result = ovfcheck(l * r)
                return universe.new_integer(result)
            except OverflowError:
                return universe.new_biginteger(
                    rbigint.fromint(l).mul(rbigint.fromint(r)))

    def prim_double_div(self, right, universe):
        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).truediv(
                right.get_embedded_biginteger())
            return universe.new_double(r)
        elif isinstance(right, Double):
            return self._to_double(universe).prim_double_div(right, universe)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            return universe.new_double(l / float(r))

    def prim_int_div(self, right, universe):
        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).floordiv(
                right.get_embedded_biginteger())
            return universe.new_biginteger(r)
        elif isinstance(right, Double):
            return self._to_double(universe).prim_int_div(right, universe)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            return universe.new_integer(l / r)

    def prim_modulo(self, right, universe):
        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).mod(
                right.get_embedded_biginteger())
            return universe.new_biginteger(r)
        elif isinstance(right, Double):
            return self._to_double(universe).prim_modulo(right, universe)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            return universe.new_integer(l % r)

    def prim_and(self, right, universe):
        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).and_(
                right.get_embedded_biginteger())
            return universe.new_biginteger(r)
        elif isinstance(right, Double):
            return self._to_double(universe).prim_and(right, universe)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            return universe.new_integer(l & r)

    def prim_equals(self, right, universe):
        if isinstance(right, BigInteger):
            result = rbigint.fromint(self._embedded_integer).eq(
                right.get_embedded_biginteger())
        elif isinstance(right, Double):
            result = self._embedded_integer == right.get_embedded_double()
        elif isinstance(right, Integer):
            l = self._embedded_integer
            r = right.get_embedded_integer()
            result = l == r
        else:
            return universe.falseObject

        if result:
            return universe.trueObject
        else:
            return universe.falseObject
