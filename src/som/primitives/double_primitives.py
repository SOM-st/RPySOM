from rpython.rlib.rfloat import round_double

from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive
from som.vmobjects.double      import Double
from som.vmobjects.integer     import Integer

import math


def _coerce_to_double(obj, universe):
    if isinstance(obj, Double):
        return obj
    if isinstance(obj, Integer):
        return universe.new_double(float(obj.get_embedded_integer()))
    raise ValueError("Cannot coerce %s to Double!" % obj)


def _asString(ivkbl, rcvr, args):
    return rcvr.prim_as_string(ivkbl.get_universe())


def _sqrt(ivkbl, rcvr, args):
    return ivkbl.get_universe().new_double(
        math.sqrt(rcvr.get_embedded_double()))


def _plus(ivkbl, rcvr, args):
    return rcvr.prim_add(args[0], ivkbl.get_universe())


def _minus(ivkbl, rcvr, args):
    return rcvr.prim_subtract(args[0], ivkbl.get_universe())


def _mult(ivkbl, rcvr, args):
    return rcvr.prim_multiply(args[0], ivkbl.get_universe())


def _doubleDiv(ivkbl, rcvr, args):
    return rcvr.prim_double_div(args[0], ivkbl.get_universe())


def _mod(ivkbl, rcvr, args):
    return rcvr.prim_modulo(args[0], ivkbl.get_universe())


def _equals(ivkbl, rcvr, args):
    return rcvr.prim_equals(args[0], ivkbl.get_universe())


def _lessThan(ivkbl, rcvr, args):
    return rcvr.prim_less_than(args[0], ivkbl.get_universe())


def _round(ivkbl, rcvr, args):
    int_value = int(round_double(rcvr.get_embedded_double(), 0))
    return ivkbl.get_universe().new_integer(int_value)


class DoublePrimitives(Primitives):

    def install_primitives(self):        
        self._install_instance_primitive(Primitive("asString", self._universe, _asString))
        self._install_instance_primitive(Primitive("round",    self._universe, _round))
        self._install_instance_primitive(Primitive("sqrt", self._universe, _sqrt))
        self._install_instance_primitive(Primitive("+",  self._universe, _plus))
        self._install_instance_primitive(Primitive("-",  self._universe, _minus))
        self._install_instance_primitive(Primitive("*",  self._universe, _mult))
        self._install_instance_primitive(Primitive("//", self._universe, _doubleDiv))
        self._install_instance_primitive(Primitive("%",  self._universe, _mod))
        self._install_instance_primitive(Primitive("=",  self._universe, _equals))
        self._install_instance_primitive(Primitive("<",  self._universe, _lessThan))
