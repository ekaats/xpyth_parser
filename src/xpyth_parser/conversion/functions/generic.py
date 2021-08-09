from src.xpyth_parser.conversion.path import PathExpression
from src.xpyth_parser.conversion.qname import Parameter


class Datatype:
    def __init__(self, arguments, qname, function_name=None):
        self.arguments = arguments
        self.qname = qname

        if function_name:
            self.function_name = function_name


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
        raise Exception(
            f"'run' function is not implemented for Function '{self.qname.__str__()}' or function is not defined"
        )

    def get_ast(self):
        """
        Returns a Python AST object

        :return:
        """
        raise NotImplemented

    def cast_parameters(self, paramlist):
        """
        Attempt to get the value of the parameter, function or just take the int value if available.

        :param paramlist:
        :return:
        """

        args = []
        for i, param in enumerate(self.arguments):
            if isinstance(param, Parameter):
                param_value = param.resolve_parameter(paramlist=paramlist)

                # Only add the parameter if a value is given.
                if param_value is not None:
                    if isinstance(param_value, list):
                        args.extend(param_value)
                    else:
                        args.append(param_value)

            elif isinstance(param, int):
                args.append(param)
            elif isinstance(param, Function):
                # need to call function to get its value. This basically turns into a nested loop

                # First call cast_parameters
                param.cast_parameters(paramlist=paramlist)

                # Get the value
                value = param.run()

                # Add this value to the list of arguments.
                args.append(value)

            # else:
            #     print("Param type not understood")

        self.cast_args.extend(args)
        return args

    def resolve_paths(self, lxml_etree):
        """
        Attempt to resolve path queries

        :param lxml_etree:
        :return:
        """

        for i, arg in enumerate(self.arguments):
            """Resolve PathExpessions and other non ast things"""
            if isinstance(arg, PathExpression):
                # Run the path expression in LXML

                if lxml_etree is not None:
                    results = lxml_etree.xpath(
                        arg.to_str(), namespaces=lxml_etree.nsmap
                    )
                    for result in results:
                        # Try to cast the value to int if applicable.
                        try:
                            val = int(result.text)
                        except:
                            val = result.text

                        self.cast_args.append(val)

                    substitute = False

                    if substitute:
                        # Substitute the old argument for the LXML elements.
                        self.arguments[i] = results
                    else:
                        # Otherwise take the argument out.
                        self.arguments.pop(i)

                else:
                    # If there is no LXML ETree, we substitute by an empty list
                    # As we would obviously not have been able to find these elements

                    self.arguments.pop(i)

            elif isinstance(arg, Parameter):
                pass

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


class Empty(Function):
    def __init__(self, arguments, qname=None):
        super().__init__(arguments, qname, function_name="empty")

    def run(self):

        if self.cast_args:
            # If there are any arguments, it is not empty.
            for arg in self.cast_args:
                if arg is None or arg == "":
                    return True

            return False

        else:
            raise Exception("Run self.cast_parameters(paramlist) first")


class Not(Function):
    def __init__(self, arguments, qname=None):
        super().__init__(arguments, qname, function_name="not")

    def run(self):

        if self.cast_args:
            for arg in self.cast_args:
                if arg is True:
                    return False  # found an argument that is true

            # Did not find a True value
            return True

        else:

            raise Exception("Run self.cast_parameters(paramlist) first")


class OrExpr:
    def __init__(self, a, b):
        self.op = "or"
        self.a = a
        self.b = b


class AndExpr:
    def __init__(self, a, b):
        self.op = "and"
        self.a = a
        self.b = b
