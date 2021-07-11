

class Function:

    def __init__(self, arguments, qname, function_name=None):
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

    def __hash__(self):
        return hash(self.__repr__())