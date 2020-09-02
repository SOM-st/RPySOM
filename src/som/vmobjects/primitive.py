from som.interp_type import is_ast_interpreter
from som.vmobjects.abstract_object import AbstractObject


class _Primitive(AbstractObject):
    _immutable_fields_ = ["_prim_fn", "_is_empty", "_signature", "_holder",
                          "_universe"]

    def __init__(self, signature_string, universe, prim_fn, is_empty=False):
        AbstractObject.__init__(self)

        self._signature = universe.symbol_for(signature_string)
        self._prim_fn   = prim_fn
        self._is_empty  = is_empty
        self._holder    = None
        self._universe  = universe

    def get_universe(self):
        return self._universe

    @staticmethod
    def is_primitive():
        return True

    @staticmethod
    def is_invokable():
        """ We use this method to identify methods and primitives """
        return True

    def get_signature(self):
        return self._signature

    def get_holder(self):
        return self._holder

    def set_holder(self, value):
        self._holder = value

    def is_empty(self):
        # By default a primitive is not empty
        return self._is_empty

    def get_class(self, universe):
        return universe.primitiveClass

    def __str__(self):
        return ("Primitive(" + self.get_holder().get_name().get_embedded_string() + ">>"
                + str(self.get_signature()) + ")")


class AstPrimitive(_Primitive):

    def invoke(self, rcvr, args):
        prim_fn = self._prim_fn
        return prim_fn(self, rcvr, args)


class BcPrimitive(_Primitive):

    def invoke(self, frame, interpreter):
        prim_fn = self._prim_fn
        prim_fn(self, frame, interpreter)


def _empty_invoke(ivkbl, _a, _b):
    """ Write a warning to the screen """
    print "Warning: undefined primitive %s called" % str(ivkbl.get_signature())


if is_ast_interpreter():
    _prim_class = AstPrimitive
else:
    _prim_class = BcPrimitive


def empty_primitive(signature_string, universe):
    """ Return an empty primitive with the given signature """
    return _prim_class(signature_string, universe, _empty_invoke, True)
