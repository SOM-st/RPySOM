try:
    from rpython.rtyper.lltypesystem import rffi
    from rpython.rtyper.lltypesystem.lltype import Signed, Unsigned
    from rpython.rtyper.lltypesystem.lloperation import llop
except ImportError:
    Signed = 1
    Unsigned = 2

    def rffi():
        pass
