




class Function:

    def __init__(self, qname, arguments, function_name=None):
        self.arguments = arguments
        self.qname = qname

        if function_name:
            self.function_name = function_name

    def run(self):
        """
        Holds 'run' function in subclasses
        """
        return NotImplemented

    def __repr__(self):
        if self.qname:
            return f"Function: {self.qname} ({self.arguments})"
        else:
            return f"Function: {type(self)} ({self.arguments})"

    def __eq__(self, other):
        if not isinstance(other, Function):
            return NotImplemented
        return self.arguments == other.arguments and self.qname == other.qname


def fn_count(*args):
    """
    Returns the number of items in a sequence.
    :param args:
    :return: int
    """

    return len(args[0])

class Count(Function):
    def __init__(self, qname, arguments):

        # Unpack tuple into separate arguments
        super().__init__(qname, arguments, function_name="count")

    def run(self):
        return fn_count(self.arguments)

class Sum(Function):
    """
    Returns a value obtained by adding together the values in self.arguments

    https://www.w3.org/TR/xpath-functions/#func-sum
    """

    def __init__(self, qname, arguments):
        super().__init__(qname, arguments, function_name="sum")

    def run(self):
        ans = 0.0
        for arg in self.arguments:

            # Any values of type xs:untypedAtomic in $arg are cast to xs:double.
            ans = ans + float(arg)
        return ans


def get_function(v):
    qname = v[0]
    args = tuple(v[1:])

    # Function name is an EQName. This name corresponds with a (buildin) function.
    # If no function is known, create a generic Function() object.
    if qname.localname == "sum":
        return Sum(arguments=args, qname=qname)
    elif qname.localname =="count":
        return Count(arguments=args, qname=qname)

    else:
        # Return generic function if the function name is not found
        return Function(arguments=args, qname=qname)