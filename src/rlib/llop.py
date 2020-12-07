try:
    from rpython.rtyper.lltypesystem.lloperation.llop import int_mod
    from rlib.lltypesystem import rffi, Signed, Unsigned

    def as_32_bit_unsigned_value(int_value):
        return rffi.cast(Signed, rffi.cast(rffi.UINT, int_value))

    def as_32_bit_signed_value(int_value):
        return rffi.cast(Signed, rffi.cast(rffi.INT, int_value))

    def unsigned_right_shift(left_val, right_val):
        u_l = rffi.cast(Unsigned, left_val)
        u_r = rffi.cast(Unsigned, right_val)

        return rffi.cast(Signed, u_l >> u_r)

except ImportError:
    "NOT_RPYTHON"
    def int_mod(_type, left, right):
        if left > 0:
            return abs(left) % abs(right)
        else:
            return 0 - (abs(left) % abs(right))

    def as_32_bit_unsigned_value(int_value):
        return int_value & 0xFFFFFFFF

    def as_32_bit_signed_value(int_value):
        is_negative = (int_value & 0x80000000) == 0x80000000
        value = int_value & 0x7FFFFFFF
        if is_negative:
            value = 0 - (0x80000000 - value)
        return value

    def unsigned_right_shift(left_val, right_val):
        return left_val >> right_val

