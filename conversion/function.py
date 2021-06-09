




class Function:

    def __init__(self, arguments):
        self.arguments = arguments

    def run(self):
        return NotImplemented

    def __repr__(self):
        return f"Function: {type(self)} ({self.arguments})"

class Sum(Function):

    def run(self):
        if len(self.arguments) > 1:

            return self.arguments[0] + self.arguments[1]



def get_function(v):
    function_name = v[0]
    args = v[1:]

    if function_name == "sum":
        return Sum(arguments=args)
    else:
        # Return generic function if the function name is not found
        return Function(arguments=args)