from .functions.aggregate import get_aggregate_function
from .functions.datetime import Date, YearMonthDuration, DayTimeDuration
from .functions.generic import Function, Not, Empty, FnQname, FnNumber


def get_function(v):
    qname = v[0]
    args = list(v[1:])



    # If no prefix is defined, FN will be assumed for function calls
    if qname.prefix is None:
        qname.prefix = "fn"

    # Function name is an EQName. This name corresponds with a (buildin) function.
    # If no function is known, create a generic Function() object.
    # if qname in ["fn:count", "fn:avg", "fn:max", "fn:min", "fn:sum"]:
    full_qname_str = qname.__repr__()

    if qname.localname in ["count", "avg", "max", "min", "sum"]:
        return get_aggregate_function(qname=qname, args=args)

    # elif qname.localname in ["empty", "not"]:
    if full_qname_str == "fn:not":
        return Not(arguments=args, qname=qname)
    elif full_qname_str == "fn:empty":
        return Empty(arguments=args, qname=qname)

    # xs:dayTimeDuration
    elif full_qname_str == "xs:date":
        return Date(arguments=args, qname=qname)
    elif full_qname_str == "xs:yearMonthDuration":
        return YearMonthDuration(arguments=args, qname=qname)
    elif full_qname_str == "xs:dayTimeDuration":
        return DayTimeDuration(arguments=args, qname=qname)
    elif full_qname_str == "xs:QName":
        return FnQname(arguments=args, qname=qname)
    elif full_qname_str in ["fn:number", "number"]:
        return FnNumber(arguments=args, qname=qname)

    else:
        # Return generic function if the function name is not found

        return Function(arguments=args, qname=qname)
