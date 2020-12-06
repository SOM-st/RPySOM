INFINITY = 1e200 * 1e200

try:
    from rpython.rlib.rfloat import formatd, DTSF_ADD_DOT_0, DTSF_STR_PRECISION, round_double

    def float_to_str(value):
        return formatd(value, "g", DTSF_STR_PRECISION, DTSF_ADD_DOT_0)

except ImportError:
    def float_to_str(value):
        return str(value)

    round_double = round
