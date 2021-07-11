from src.xpyth_parser.conversion.qname import Parameter


class Function:

    def __init__(self, arguments, qname, function_name=None):
        self.arguments = arguments
        self.qname = qname

        if function_name:
            self.function_name = function_name

        # Set cast args to an empty list. Will be filled by self.cast_parameters()
        self.cast_args = []

    def run(self):
        """
        Holds 'run' function in subclasses
        """
        raise NotImplemented

    def get_ast(self):
        """
        Returns a Python AST object

        :return:
        """
        raise NotImplemented

    def cast_parameters(self, paramlist):
        args = []
        for i, param in enumerate(self.arguments):
            if isinstance(param, Parameter):
                param_value = param.resolve_parameter(paramlist=paramlist)
                if isinstance(param_value, list):
                    args.extend(param_value)
                else:
                    args.append(param_value)

            elif isinstance(param, int):
                args.append(param)
            else:
                print("Param type not understood")

        self.cast_args = args
        return args

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