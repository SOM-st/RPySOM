try:
    from rpython.rtyper.lltypesystem import lltype, rffi
    from rpython.rtyper.lltypesystem.lloperation import llop
except ImportError:
    def lltype():
        pass

    def rffi():
        pass

    def llop():
        pass
