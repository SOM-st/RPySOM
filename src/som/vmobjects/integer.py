from rpython.rlib.rarithmetic import ovfcheck
from rpython.rlib.rbigint import rbigint, _divrem
from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.rtyper.lltypesystem.lloperation import llop

from som.vmobjects.abstract_object import AbstractObject
from som.vm.globals import trueObject, falseObject


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
        right = frame.top()
        frame.pop()
        frame.pop()
        frame.push(self.prim_add(right))

    def quick_multiply(self, from_method, frame, interpreter, bytecode_index):
        right = frame.top()
        frame.pop()
        frame.pop()
        frame.push(self.prim_multiply(right))

    def quick_subtract(self, from_method, frame, interpreter, bytecode_index):
        right = frame.top()
        frame.pop()
        frame.pop()
        frame.push(self.prim_subtract(right))

    def _to_double(self):
        from .double import Double
        return Double(float(self._embedded_integer))

    def prim_less_than(self, right):
        from .double import Double
        from .biginteger import BigInteger
        # Check second parameter type:
        if isinstance(right, BigInteger):
            result = rbigint.fromint(self._embedded_integer).lt(
                right.get_embedded_biginteger())
        elif isinstance(right, Double):
            return self._to_double().prim_less_than(right)
        else:
            result = self._embedded_integer < right.get_embedded_integer()

        if result:
            return trueObject
        else:
            return falseObject

    def prim_less_than_or_equal(self, right):
        from .double import Double
        from .biginteger import BigInteger
        # Check second parameter type:
        if isinstance(right, BigInteger):
            result = rbigint.fromint(self._embedded_integer).le(
                right.get_embedded_biginteger())
        elif isinstance(right, Double):
            return self._to_double().prim_less_than_or_equal(right)
        else:
            result = self._embedded_integer <= right.get_embedded_integer()

        if result:
            return trueObject
        else:
            return falseObject

    def prim_greater_than(self, right):
        from .double import Double
        from .biginteger import BigInteger
        # Check second parameter type:
        if isinstance(right, BigInteger):
            result = rbigint.fromint(self._embedded_integer).gt(
                right.get_embedded_biginteger())
        elif isinstance(right, Double):
            return self._to_double().prim_greater_than(right)
        else:
            result = self._embedded_integer > right.get_embedded_integer()

        if result:
            return trueObject
        else:
            return falseObject

    def prim_as_string(self):
        from .string import String
        return String(str(self._embedded_integer))

    def prim_abs(self):
        return Integer(abs(self._embedded_integer))

    def prim_as_32_bit_signed_value(self):
        val = rffi.cast(lltype.Signed, rffi.cast(rffi.INT, self._embedded_integer))
        return Integer(val)

    def prim_max(self, right):
        from .biginteger import BigInteger
        if isinstance(right, BigInteger):
            left = rbigint.fromint(self._embedded_integer)
            if right.get_embedded_biginteger().gt(left):
                return right
            return self
        assert isinstance(right, Integer)
        if right.get_embedded_integer() > self._embedded_integer:
            return right
        return self

    def prim_add(self, right):
        from .double import Double
        from .biginteger import BigInteger
        if isinstance(right, BigInteger):
            return BigInteger(
                right.get_embedded_biginteger().add(
                    rbigint.fromint(self._embedded_integer)))
        elif isinstance(right, Double):
            return self._to_double().prim_add(right)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            try:
                result = ovfcheck(l + r)
                return Integer(result)
            except OverflowError:
                return BigInteger(
                    rbigint.fromint(l).add(rbigint.fromint(r)))

    def prim_subtract(self, right):
        from .double import Double
        from .biginteger import BigInteger
        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).sub(
                right.get_embedded_biginteger())
            return BigInteger(r)
        elif isinstance(right, Double):
            return self._to_double().prim_subtract(right)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            try:
                result = ovfcheck(l - r)
                return Integer(result)
            except OverflowError:
                return BigInteger(
                    rbigint.fromint(l).sub(rbigint.fromint(r)))

    def prim_multiply(self, right):
        from .double import Double
        from .biginteger import BigInteger

        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).mul(
                right.get_embedded_biginteger())
            return BigInteger(r)
        elif isinstance(right, Double):
            return self._to_double().prim_multiply(right)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            try:
                result = ovfcheck(l * r)
                return Integer(result)
            except OverflowError:
                return BigInteger(
                    rbigint.fromint(l).mul(rbigint.fromint(r)))

    def prim_double_div(self, right):
        from .double import Double
        from .biginteger import BigInteger

        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).truediv(
                right.get_embedded_biginteger())
            return Double(r)
        elif isinstance(right, Double):
            return self._to_double().prim_double_div(right)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            return Double(l / float(r))

    def prim_int_div(self, right):
        from .double import Double
        from .biginteger import BigInteger

        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).floordiv(
                right.get_embedded_biginteger())
            return BigInteger(r)
        elif isinstance(right, Double):
            return self._to_double().prim_int_div(right)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            return Integer(l / r)

    def prim_modulo(self, right):
        from .double import Double
        from .biginteger import BigInteger

        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).mod(
                right.get_embedded_biginteger())
            return BigInteger(r)
        elif isinstance(right, Double):
            return self._to_double().prim_modulo(right)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            return Integer(l % r)

    def prim_remainder(self, right):
        from .double import Double
        from .biginteger import BigInteger

        if isinstance(right, BigInteger):
            d, r = _divrem(rbigint.fromint(self._embedded_integer),
                           right.get_embedded_biginteger())
            return BigInteger(r)
        elif isinstance(right, Double):
            return self._to_double().prim_remainder(right)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            return Integer(llop.int_mod(lltype.Signed, l, r))

    def prim_and(self, right):
        from .double import Double
        from .biginteger import BigInteger

        if isinstance(right, BigInteger):
            r = rbigint.fromint(self._embedded_integer).and_(
                right.get_embedded_biginteger())
            return BigInteger(r)
        elif isinstance(right, Double):
            return self._to_double().prim_and(right)
        else:
            l = self._embedded_integer
            r = right.get_embedded_integer()
            return Integer(l & r)

    def prim_equals(self, right):
        from .double import Double
        from .biginteger import BigInteger

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
            return falseObject

        if result:
            return trueObject
        else:
            return falseObject

    def prim_unequals(self, right):
        from .double import Double
        from .biginteger import BigInteger

        if isinstance(right, BigInteger):
            result = rbigint.fromint(self._embedded_integer).ne(
                right.get_embedded_biginteger())
        elif isinstance(right, Double):
            result = self._embedded_integer != right.get_embedded_double()
        elif isinstance(right, Integer):
            l = self._embedded_integer
            r = right.get_embedded_integer()
            result = l != r
        else:
            return trueObject

        if result:
            return trueObject
        else:
            return falseObject
