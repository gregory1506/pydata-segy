from numba import vectorize()

@vectorize(['float32(uint32)'])
def ibm32toieee32(self, data):
    if data == 0:
        return 0.0
    sign = data >> 31 & 0x01
    exponent = data >> 24 & 0x7f
    mantissa = (data & 0x00ffffff) / float(pow(2, 24))
    return (1 - 2 * sign) * mantissa * pow(16.0, exponent - 64)