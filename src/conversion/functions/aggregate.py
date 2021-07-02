from src.conversion.functions.generic import Function


class Count(Function):
    """
    Returns the number of items in a sequence.
    """

    def __init__(self, arguments, qname=None):
        super().__init__(arguments, qname, function_name="count")

    def run(self):
        return len(self.arguments)


class Avg(Function):
    """
    Returns the average of the values in the input sequence $arg, that is,
    the sum of the values divided by the number of values.
    """

    def __init__(self, arguments, qname=None):

        # Unpack tuple into separate arguments
        super().__init__(arguments, qname, function_name="count")

    def run(self):
        return sum(self.arguments) / len(self.arguments)

class Max(Function):
    """
    Returns a value that is equal to the highest value appearing in the input sequence.
    """

    def __init__(self, arguments, qname=None):

        # Unpack tuple into separate arguments
        super().__init__(arguments, qname, function_name="count")

    def run(self):
        return max(self.arguments)


class Min(Function):
    """
    Returns a value that is equal to the lowest value appearing in the input sequence.
    """

    def __init__(self, arguments, qname=None):

        # Unpack tuple into separate arguments
        super().__init__(arguments, qname, function_name="count")

    def run(self):
        return min(self.arguments)


class Sum(Function):
    """
    Returns a value obtained by adding together the values in self.arguments

    https://www.w3.org/TR/xpath-functions/#func-sum
    """

    def __init__(self, arguments, qname=None):
        super().__init__(arguments, qname, function_name="sum")

    def run(self):
        return sum(self.arguments)





def get_aggregate_function(args, qname):
    # qname = v[0]
    # args = tuple(v[1:])

    # Function name is an EQName. This name corresponds with a (build-in) function.
    # If no function is known, create a generic Function() object.


    if qname.__repr__() == "fn:count":
        return Count(arguments=args, qname=qname)
    elif qname.__repr__() == "fn:avg":
        return Avg(arguments=args, qname=qname)
    elif qname.__repr__() == "fn:max":
        return Max(arguments=args, qname=qname)
    elif qname.__repr__() == "fn:min":
        return Min(arguments=args, qname=qname)
    elif qname.__repr__() == "fn:sum":
        return Sum(arguments=args, qname=qname)
    else:
        return None

