from decimal import Decimal


def str_to_int(value):
    i = value[0]
    return int(i)


def str_to_dec(value):
    i = value[0]
    return Decimal(i)


def str_to_float(value):

    if len(value) > 1:
        # There is an exponent
        if value[2] in ["-", "+"]:
            exp_sign = value[2]
            exp = value[3]

        else:
            # If there is no sign, we need to get the exponent from [2]
            exp_sign = ""
            exp = value[2]
        return float(f"{value[0]}{value[1]}{exp_sign}{exp}")
    return float(value[0])
