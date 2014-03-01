from rpython.rlib.objectmodel import compute_identity_hash

from som.primitives.primitives import Primitives

from som.vmobjects.object    import Object  
from som.vmobjects.primitive import Primitive
from som.vmobjects.array     import Array 


def _equals(ivkbl, frame, rcvr, args):
    op1 = args[0]
    op2 = rcvr
    if op1 is op2:
        return ivkbl.get_universe().trueObject
    else:
        return ivkbl.get_universe().falseObject


def _hashcode(ivkbl, frame, rcvr, args):
    return ivkbl.get_universe().new_integer(
        compute_identity_hash(rcvr))


def _objectSize(ivkbl, frame, rcvr, args):
    size = 0
    
    if isinstance(rcvr, Object):
        size = rcvr.get_number_of_fields()
    elif isinstance(rcvr, Array):
        size = rcvr.get_number_of_indexable_fields()

    return ivkbl.get_universe().new_integer(size)


def _perform(ivkbl, frame, rcvr, args):
    selector = args[0]

    invokable = rcvr.get_class(ivkbl.get_universe()).lookup_invokable(selector)
    return invokable.invoke(frame, rcvr, None)


def _performInSuperclass(ivkbl, frame, rcvr, args):
    clazz    = args[1]
    selector = args[0]

    invokable = clazz.lookup_invokable(selector)
    return invokable.invoke(frame, rcvr, None)


def _performWithArguments(ivkbl, frame, rcvr, arguments):
    arg_arr  = arguments[1].get_indexable_fields()
    selector = arguments[0]

    invokable = rcvr.get_class(ivkbl.get_universe()).lookup_invokable(selector)
    return invokable.invoke(frame, rcvr, arg_arr)


def _instVarAt(ivkbl, frame, rcvr, args):
    idx  = args[0]
    return rcvr.get_field(idx.get_embedded_integer() - 1)


def _instVarAtPut(ivkbl, frame, rcvr, args):
    val  = args[1]
    idx  = args[0]
    rcvr.set_field(idx.get_embedded_integer() - 1, val)
    return val


def _halt(ivkbl, frame, rcvr, args):
    # noop
    print "BREAKPOINT"
    return rcvr


def _class(ivkbl, frame, rcvr, args):
    return rcvr.get_class(ivkbl.get_universe())
    


class ObjectPrimitives(Primitives):
    
    def install_primitives(self):
        self._install_instance_primitive(Primitive("==", self._universe, _equals))
        self._install_instance_primitive(Primitive("hashcode", self._universe, _hashcode))
        self._install_instance_primitive(Primitive("objectSize", self._universe, _objectSize))
        self._install_instance_primitive(Primitive("perform:", self._universe, _perform))
        self._install_instance_primitive(Primitive("perform:inSuperclass:", self._universe, _performInSuperclass))
        self._install_instance_primitive(Primitive("perform:withArguments:", self._universe, _performWithArguments))
        self._install_instance_primitive(Primitive("instVarAt:", self._universe, _instVarAt))
        self._install_instance_primitive(Primitive("instVarAt:put:", self._universe, _instVarAtPut))
        
        self._install_instance_primitive(Primitive("halt", self._universe, _halt))
        self._install_instance_primitive(Primitive("class", self._universe, _class))

