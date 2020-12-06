try:
    from rpython.rlib.rarithmetic import ovfcheck, LONG_BIT
    from rpython.rlib.rbigint.rbigint import fromint as bigint_from_int
    from rpython.rlib.rbigint import _divrem as divrem, rbigint as bigint_type
    from rpython.rlib.rarithmetic import string_to_int
    from rpython.rlib.rstring import ParseStringOverflowError
    int_type = int
except ImportError:
    def ovfcheck(value):
        return value

    def bigint_from_int(value):
        return value

    def divrem(a, b):
        raise Exception("not yet implemented")

    string_to_int = int

    class ParseStringOverflowError(Exception):
        def __init__(self, parser):
            self.parser = parser

    LONG_BIT = 0x8000000000000000

    try:
        int_type = (int, long)
        bigint_type = long
    except NameError:
        int_type = int
        bigint_type = int
