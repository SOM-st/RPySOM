try:
    from rpython.rtyper.lltypesystem import rffi
    from rpython.rtyper.lltypesystem.lltype import Signed, Unsigned
    from rpython.rtyper.lltypesystem.lloperation import llop
except ImportError:
    "NOT_RPYTHON"
    Signed = 1
    Unsigned = 2

    def rffi():
        pass
