from som.primitives.primitives import Primitives
from som.vmobjects.primitive import Primitive

def _concat(ivkbl, frame, interpreter):
    argument = frame.pop()
    rcvr     = frame.pop()
    frame.push(interpreter.get_universe().new_string(rcvr.get_embedded_string()
                                   + argument.get_embedded_string()))

def _asSymbol(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().symbol_for(rcvr.get_embedded_string()))

def _length(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_integer(len(rcvr.get_embedded_string())))

def _equals(ivkbl, frame, interpreter):
    op1 = frame.pop()
    op2 = frame.pop() # rcvr
    if op1.get_class() == interpreter.get_universe().stringClass:
        if op1.get_embedded_string() == op2.get_embedded_string():
            frame.push(interpreter.get_universe().trueObject)
            return
    frame.push(interpreter.get_universe().falseObject)

def _substring(ivkbl, frame, interpreter):
    end   = frame.pop()
    start = frame.pop()
    rcvr  = frame.pop()

    try:
        frame.push(interpreter.get_universe().new_string(rcvr.get_embedded_string()[
                                start.get_embedded_integer():end.get_embedded_integer() + 1]))
    except IndexError, e:
        frame.push(interpreter.get_universe().new_string("Error - index out of bounds: %s" % e))

def _hashcode(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_integer(hash(rcvr.get_embedded_string())))

class StringPrimitives(Primitives):
    
    def install_primitives(self):        
        self._install_instance_primitive(Primitive("concatenate:",          self._universe, _concat))
        self._install_instance_primitive(Primitive("asSymbol",              self._universe, _asSymbol))
        self._install_instance_primitive(Primitive("length",                self._universe, _length))
        self._install_instance_primitive(Primitive("=",                     self._universe, _equals))
        self._install_instance_primitive(Primitive("primSubstringFrom:to:", self._universe, _substring))
        self._install_instance_primitive(Primitive("hashcode",              self._universe, _hashcode))
