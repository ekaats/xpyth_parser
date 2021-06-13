from conversion.functions.generic import Function


class Count(Function):
    """
    Returns the number of items in a sequence.
    """

    def __init__(self, qname, arguments):
        super().__init__(qname, arguments, function_name="count")

    def run(self):
        return len(self.arguments)


class Avg(Function):
    """
    Returns the average of the values in the input sequence $arg, that is,
    the sum of the values divided by the number of values.
    """

    def __init__(self, qname, arguments):

        # Unpack tuple into separate arguments
        super().__init__(qname, arguments, function_name="count")

    def run(self):
        return sum(self.arguments) / len(self.arguments)

class Max(Function):
    """
    Returns a value that is equal to the highest value appearing in the input sequence.
    """

    def __init__(self, qname, arguments):

        # Unpack tuple into separate arguments
        super().__init__(qname, arguments, function_name="count")

    def run(self):
        return max(self.arguments)


class Min(Function):
    """
    Returns a value that is equal to the lowest value appearing in the input sequence.
    """

    def __init__(self, qname, arguments):

        # Unpack tuple into separate arguments
        super().__init__(qname, arguments, function_name="count")

    def run(self):
        return min(self.arguments)


class Sum(Function):
    """
    Returns a value obtained by adding together the values in self.arguments

    https://www.w3.org/TR/xpath-functions/#func-sum
    """

    def __init__(self, qname, arguments):
        super().__init__(qname, arguments, function_name="sum")

    def run(self):
        return sum(self.arguments)





def get_aggregate_function(qname, args):
    # qname = v[0]
    # args = tuple(v[1:])

    # Function name is an EQName. This name corresponds with a (buildin) function.
    # If no function is known, create a generic Function() object.

    if qname.localname == "count":
        return Count(arguments=args, qname=qname)
    elif qname.localname == "avg":
        return Avg(arguments=args, qname=qname)
    elif qname.localname == "max":
        return Max(arguments=args, qname=qname)
    elif qname.localname == "min":
        return Min(arguments=args, qname=qname)
    elif qname.localname == "sum":
        return Sum(arguments=args, qname=qname)
    else:
        return None

