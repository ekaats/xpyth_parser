from conversion.functions.aggregate import get_aggregate_function
from conversion.functions.generic import Function


def get_function(v):
    qname = v[0]
    args = tuple(v[1:])

    # Function name is an EQName. This name corresponds with a (buildin) function.
    # If no function is known, create a generic Function() object.
    # if qname in ["fn:count", "fn:avg", "fn:max", "fn:min", "fn:sum"]:
    if qname.localname in ["count", "avg", "max", "min", "sum"]:
        return get_aggregate_function(qname=qname, args=args)

    else:
        # Return generic function if the function name is not found
        return Function(arguments=args, qname=qname)