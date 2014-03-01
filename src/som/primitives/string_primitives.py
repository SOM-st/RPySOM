from rpython.rlib.objectmodel import compute_identity_hash

from som.primitives.primitives import Primitives
from som.vmobjects.primitive import Primitive


def _concat(ivkbl, frame, rcvr, args):
    argument = args[0]
    return ivkbl.get_universe().new_string(rcvr.get_embedded_string()
                                           + argument.get_embedded_string())

def _asSymbol(ivkbl, frame, rcvr, args):
    return ivkbl.get_universe().symbol_for(rcvr.get_embedded_string())


def _length(ivkbl, frame, rcvr, args):
    return ivkbl.get_universe().new_integer(len(rcvr.get_embedded_string()))


def _equals(ivkbl, frame, rcvr, args):
    op1 = args[0]
    op2 = rcvr
    universe = ivkbl.get_universe()
    if op1.get_class(universe) == universe.stringClass:
        if op1.get_embedded_string() == op2.get_embedded_string():
            return universe.trueObject
    return universe.falseObject


def _substring(ivkbl, frame, rcvr, args):
    end   = args[1]
    start = args[0]

    s      = start.get_embedded_integer() - 1
    e      = end.get_embedded_integer()
    string = rcvr.get_embedded_string()
    
    if s < 0 or s >= len(string) or e > len(string) or e < s: 
        return ivkbl.get_universe().new_string("Error - index out of bounds")
    else:
        return ivkbl.get_universe().new_string(string[s:e])


def _hashcode(ivkbl, frame, rcvr, args):
    return ivkbl.get_universe().new_integer(
        compute_identity_hash(rcvr.get_embedded_string()))


class StringPrimitives(Primitives):
    
    def install_primitives(self):        
        self._install_instance_primitive(Primitive("concatenate:",          self._universe, _concat))
        self._install_instance_primitive(Primitive("asSymbol",              self._universe, _asSymbol))
        self._install_instance_primitive(Primitive("length",                self._universe, _length))
        self._install_instance_primitive(Primitive("=",                     self._universe, _equals))
        self._install_instance_primitive(Primitive("primSubstringFrom:to:", self._universe, _substring))
        self._install_instance_primitive(Primitive("hashcode",              self._universe, _hashcode))
