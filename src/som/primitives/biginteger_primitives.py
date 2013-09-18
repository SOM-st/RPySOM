from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive
from som.vmobjects.integer     import Integer
 
import math

class BigIntegerPrimitives(Primitives):

    def install_primitives(self):
        def _asString(ivkbl, frame, interpreter):
            rcvr = frame.pop()
            frame.push(self._universe.new_string(str(rcvr.get_embedded_biginteger())))
        self._install_instance_primitive(Primitive("asString", self._universe, _asString))
        
        def _sqrt(ivkbl, frame, interpreter):
            rcvr = frame.pop()
            frame.push(self._universe.new_double(
                               math.sqrt(rcvr.get_embedded_biginteger())))
        self._install_instance_primitive(Primitive("sqrt", self._universe, _sqrt))
        
        def _plus(ivkbl, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()
        
            # Do operation and perform conversion to Integer if required
            result = left.get_embedded_biginteger() + right_obj.get_embedded_value()
            if Integer.value_fits(result):
                frame.push(self._universe.new_integer(result))
            else:
                frame.push(self._universe.new_biginteger(result))
        self._install_instance_primitive(Primitive("+", self._universe, _plus))
        
        def _minus(ivkbl, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()
        
            # Do operation and perform conversion to Integer if required
            result = left.get_embedded_biginteger() - right_obj.get_embedded_value()
            if Integer.value_fits(result):
                frame.push(self._universe.new_integer(result))
            else:
                frame.push(self._universe.new_biginteger(result))
        self._install_instance_primitive(Primitive("-", self._universe, _minus))

        def _mult(ivkbl, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()

            # Do operation and perform conversion to Integer if required
            result = left.get_embedded_biginteger() * right_obj.get_embedded_value()
            if Integer.value_fits(result):
                frame.push(self._universe.new_integer(result))
            else:
                frame.push(self._universe.new_biginteger(result))
        self._install_instance_primitive(Primitive("*", self._universe, _mult))

        def _div(ivkbl, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()

            # Do operation and perform conversion to Integer if required
            result = left.get_embedded_biginteger() / right_obj.get_embedded_value()
            if Integer.value_fits(result):
                frame.push(self._universe.new_integer(result))
            else:
                frame.push(self._universe.new_biginteger(result))
        self._install_instance_primitive(Primitive("/", self._universe, _div))

        def _mod(ivkbl, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()

            # Do operation:
            frame.push(self._universe.new_biginteger(left.get_embedded_biginteger() % right_obj.get_embedded_value()))
        self._install_instance_primitive(Primitive("%", self._universe, _mod))
    
        def _and(ivkbl, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()

            # Do operation:
            frame.push(self._universe.new_biginteger(left.get_embedded_biginteger() & right_obj.get_embedded_value()))
        self._install_instance_primitive(Primitive("&", self._universe, _and))

        def _equals(ivkbl, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()

            # Do operation:
            if left.get_embedded_biginteger() == right_obj.get_embedded_value():
                frame.push(self._universe.trueObject)
            else:
                frame.push(self._universe.falseObject)
        self._install_instance_primitive(Primitive("=", self._universe, _equals))

        def _lessThan(ivkbl, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()
        
            # Do operation:
            if left.get_embedded_biginteger() < right_obj.get_embedded_value():
                frame.push(self._universe.trueObject)
            else:
                frame.push(self._universe.falseObject)
        self._install_instance_primitive(Primitive("<", self._universe, _lessThan))
