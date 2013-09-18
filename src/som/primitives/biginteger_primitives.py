from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive

import math

class BigIntegerPrimitives(Primitives):

    def install_primitives(self):
        def _asString(self, frame, interpreter):
            rcvr = frame.pop()
            frame.push(self._universe.new_string(str(rcvr.get_embedded_biginteger())))
        self._install_instance_primitive(Primitive("asString", self._universe, _asString))
        
        def _sqrt(self, frame, interpreter):
            rcvr = frame.pop()
            frame.push(self._universe.new_double(
                               math.sqrt(rcvr.get_embedded_biginteger())))
        self._install_instance_primitive(Primitive("sqrt", self._universe, _sqrt))
        
        def _plus(self, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()
        
            # Check second parameter type:
            if isinstance(right_obj, int):
                # Second operand was Integer
                right = self._universe.new_biginteger(right_obj.get_embedded_integer())
            else:
                right = right_obj
        
            # Do operation and perform conversion to Integer if required
            result = left.get_embedded_biginteger() + right.get_embedded_biginteger()
            if isinstance(result, long):
                frame.push(self._universe.new_biginteger(result))
            else:
                frame.push(self._universe.new_integer(result))
        self._install_instance_primitive(Primitive("+", self._universe, _plus))
        
        def _minus(self, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()
        
            # Check second parameter type:
            if isinstance(right_obj, int):
                # Second operand was Integer
                right = self._universe.new_biginteger(right_obj.get_embedded_integer())
            else:
                right = right_obj
        

            # Do operation and perform conversion to Integer if required
            result = left.get_embedded_biginteger() - right.get_embedded_biginteger()
            if isinstance(result, long):
                frame.push(self._universe.new_biginteger(result))
            else:
                frame.push(self._universe.new_integer(result.intValue()));
        self._install_instance_primitive(Primitive("-", self._universe, _minus))

        def _mult(self, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()

            # Check second parameter type:
            if isinstance(right_obj, int):
                # Second operand was Integer
                right = self._universe.new_biginteger(right_obj.get_embedded_integer())
            else:
                right = right_obj

            # Do operation and perform conversion to Integer if required
            result = left.get_embedded_biginteger() * right.get_embedded_biginteger()
            if isinstance(result, long):
                frame.push(self._universe.new_biginteger(result))
            else:
                frame.push(self._universe.new_integer(result))
        self._install_instance_primitive(Primitive("*", self._universe, _mult))

        def _div(self, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()

            # Check second parameter type:
            if isinstance(right_obj, int):
                # Second operand was Integer
                right = self._universe.new_biginteger(right_obj.get_embedded_integer())
            else:
                right = right_obj

            # Do operation and perform conversion to Integer if required
            result = left.get_embedded_biginteger() / right.get_embedded_biginteger()
            if isinstance(result, long):
                frame.push(self._universe.new_biginteger(result))
            else:
                frame.push(self._universe.new_integer(result))
        self._install_instance_primitive(Primitive("/", self._universe, _div))

        def _mod(self, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()

            # Check second parameter type:
            if isinstance(right_obj, int):
                # Second operand was Integer
                right = self._universe.new_biginteger(right_obj.get_embedded_integer())
            else:
                right = right_obj

            # Do operation:
            frame.push(self._universe.new_biginteger(left.get_embedded_biginteger() % right.get_embedded_biginteger()))
        self._install_instance_primitive(Primitive("%", self._universe, _mod))
    
        def _and(self, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()

            # Check second parameter type:
            if isinstance(right_obj, int):
                # Second operand was Integer
                right = self._universe.new_biginteger(right_obj.get_embedded_integer())
            else:
                right = right_obj

            # Do operation:
            frame.push(self._universe.new_biginteger(left.get_embedded_biginteger() & right.get_embedded_biginteger()))
        self._install_instance_primitive(Primitive("&", self._universe, _and))

        def _equals(self, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()

            # Check second parameter type:
            if isinstance(right_obj, int):
                # Second operand was Integer
                right = self._universe.new_biginteger(right_obj.get_embedded_integer())
            else:
                right = right_obj

            # Do operation:
            if left.get_embedded_biginteger() == right.get_embedded_biginteger():
                frame.push(self._universe.trueObject)
            else:
                frame.push(self._universe.falseObject)
        self._install_instance_primitive(Primitive("=", self._universe, _equals))

        def _lessThan(self, frame, interpreter):
            right_obj = frame.pop()
            left      = frame.pop()

            # Check second parameter type:
            if isinstance(right_obj, int):
                # Second operand was Integer
                right = self._universe.new_biginteger(right_obj.get_embedded_integer())
            else:
                right = right_obj
        
            # Do operation:
            if left.get_embedded_biginteger() < right.get_embedded_biginteger():
                frame.push(self._universe.trueObject)
            else:
                frame.push(self._universe.falseObject)
        self._install_instance_primitive(Primitive("<", self._universe, _lessThan))
