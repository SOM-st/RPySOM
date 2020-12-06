import types

try:
    from rpython.rlib.objectmodel import we_are_translated, compute_identity_hash, compute_hash, instantiate
except ImportError:
    def we_are_translated():
        return False

    def compute_identity_hash(x):
        assert x is not None
        return object.__hash__(x)

    def compute_hash(x):
        if isinstance(x, (str, unicode)):
            return hash(x)
        if isinstance(x, int):
            return x
        if isinstance(x, float):
            return hash(x)
        if isinstance(x, tuple):
            return hash(x)
        if x is None:
            return 0
        return compute_identity_hash(x)

    def instantiate(cls, nonmovable=False):
        "Create an empty instance of 'cls'."
        if isinstance(cls, type):
            return cls.__new__(cls)
        else:
            return types.InstanceType(cls)
