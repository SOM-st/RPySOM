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


def _asString(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.prim_as_string(interpreter.get_universe()))


def _sqrt(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_double(math.sqrt(
        rcvr.get_embedded_double())))


def _plus(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_add(right, interpreter.get_universe()))


def _minus(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_subtract(right, interpreter.get_universe()))


def _mult(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_multiply(right, interpreter.get_universe()))


def _doubleDiv(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_double_div(right, interpreter.get_universe()))


def _mod(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_modulo(right, interpreter.get_universe()))


def _equals(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_equals(right, interpreter.get_universe()))


def _lessThan(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_less_than(right, interpreter.get_universe()))


def _round(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    int_value = int(round_double(rcvr.get_embedded_double(), 0))
    frame.push(interpreter.get_universe().new_integer(int_value))


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
