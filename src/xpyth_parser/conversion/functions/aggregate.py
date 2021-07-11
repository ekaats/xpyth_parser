from .generic import Function
from ..qname import Parameter


class Count(Function):
    """
    Returns the number of items in a sequence.
    """

    def __init__(self, arguments, qname=None):
        super().__init__(arguments, qname, function_name="count")

    def run(self):

        if self.cast_args:
            return len(self.cast_args)

        else:

            try:
                return len(self.arguments)
            except TypeError:
                raise Exception("Run self.cast_parameters(paramlist) first")



class Avg(Function):
    """
    Returns the average of the values in the input sequence $arg, that is,
    the sum of the values divided by the number of values.
    """

    def __init__(self, arguments, qname=None):

        # Unpack tuple into separate arguments
        super().__init__(arguments, qname, function_name="count")

    def run(self):
        if self.cast_args:
            return sum(self.cast_args) / len(self.cast_args)

        else:
            try:
                return sum(self.arguments) / len(self.arguments)
            except TypeError:
                raise Exception("Run self.cast_parameters(paramlist) first")


class Max(Function):
    """
    Returns a value that is equal to the highest value appearing in the input sequence.
    """

    def __init__(self, arguments, qname=None):

        # Unpack tuple into separate arguments
        super().__init__(arguments, qname, function_name="count")

    def run(self):
        if self.cast_args:
            return max(self.cast_args)

        else:
            try:
                return max(self.arguments)
            except TypeError:
                raise Exception("Run self.cast_parameters(paramlist) first")



class Min(Function):
    """
    Returns a value that is equal to the lowest value appearing in the input sequence.
    """

    def __init__(self, arguments, qname=None):

        # Unpack tuple into separate arguments
        super().__init__(arguments, qname, function_name="count")

    def run(self):
        if self.cast_args:
            return min(self.cast_args)

        else:
            try:
                return min(self.arguments)
            except TypeError:
                raise Exception("Run self.cast_parameters(paramlist) first")


class Sum(Function):
    """
    Returns a value obtained by adding together the values in self.arguments

    https://www.w3.org/TR/xpath-functions/#func-sum
    """

    def __init__(self, arguments, qname=None):
        super().__init__(arguments, qname, function_name="sum")

    def run(self):
        if self.cast_args:
            return sum(self.cast_args)

        else:
            try:
                return sum(self.arguments)
            except TypeError:
                raise Exception("Run self.cast_parameters(paramlist) first")

    def get_ast(self, paramlist=None):
        for i, argument in enumerate(self.arguments):
            if isinstance(argument, Parameter):
                # self.arguments[i] = argument.get_ast_node(paramlist=paramlist)
                newarg = argument.resolve_parameter(paramlist=paramlist)
                print(newarg)


def get_aggregate_function(args, qname):
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

