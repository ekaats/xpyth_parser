import logging
from typing import Union, Optional
from ..qname import Parameter, QName


class FunctionRegistry:
    _instance = None
    functions = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, custom_functions: Optional[dict] = None, overwrite_functions: Optional[bool] = False):
        """
        Initialise the FunctionRegistry. In this singleton we keep track of all available functions.
        They are used by wrapping into the Function class.

        :param custom_functions:
        """

        if custom_functions is not None:
            for function_name, function in custom_functions.items():
                if function_name not in self.functions.keys():
                    self.functions[function_name] = function
                elif overwrite_functions is True:
                    # Only overwrite functions if this is explicitly set
                    self.functions[function_name] = function

    def get_function(self, qname: Union[QName, str]):

        if isinstance(qname, QName):
            if qname.__repr__() in self.functions.keys():
                return self.functions[qname.__repr__()]
        else:
            if qname in self.functions.keys():
                return self.functions[qname]

        return None

class Function:
    def __init__(self, arguments, qname, function_name=None):
        self.arguments = arguments
        self.qname = qname

        if function_name:
            self.function_name = function_name

        # Set cast args to an empty list. Will be filled by self.cast_parameters()
        self.cast_args = []

        self.function_registry = FunctionRegistry()

    def run(self):
        """
        Holds 'run' function in subclasses
        """
        function = self.function_registry.get_function(qname=self.qname)
        if function is not None:
            self.run = function
            # todo: maybe better to not add the function to the object, but just pass arguments to the function
            #  that would be a lot more easy to work with for third party functions
            return self.run(self)


        raise Exception(
            f"'run' function is not implemented for Function '{self.qname.__str__()}' or function is not defined"
        )

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
            else:
                logging.warning(f"Parameter type not castable: {type(param)}")

        self.cast_args.extend(args)
        return args

    def resolve_paths(self, lxml_etree):
        """
        Attempt to resolve path queries

        :param lxml_etree:
        :return:
        """

        for i, arg in enumerate(self.arguments):

            if hasattr(arg, "resolve_path"):
            # if isinstance(arg, path.PathExpression):
                if lxml_etree is None:
                    # If there is no LXML ETree, we substitute by an empty list
                    # As we would obviously not have been able to find these elements
                    self.arguments.pop(i)
                else:
                    # Substitute the old argument for the LXML elements.
                    resolved_args = arg.resolve_path(lxml_etree=lxml_etree)
                    if isinstance(resolved_args, list):
                        # If a list is returned, we need to take out the original parameter and add
                        #  all found values to list
                        self.arguments.pop(i)
                        self.arguments.extend(resolved_args)

                        # If a single value has been returned, we can just replace the parameter
                    else:
                        self.arguments[i] = resolved_args

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

class FnQname(Function):
    def __init__(self, arguments, qname=None):
        # Returns an xs:QName value formed using a supplied namespace URI and lexical QName.
        super().__init__(arguments, qname, function_name="qname")

    def run(self):
        # Returns an xs:QName value formed using a supplied namespace URI and lexical QName.

        if len(self.arguments) == 1:
            prefix, localname = str(self.arguments[0]).split(":", 1)
            return QName(prefix=prefix, localname=localname)
        elif len(self.arguments) == 2:
            # If a namespace is given, add that to the QName as well
            prefix, localname = str(self.arguments[1]).split(":", 1)
            return QName(prefix=prefix, localname=localname, namespace=self.arguments[0])

class FnNumber(Function):
    # https://www.w3.org/TR/xpath-functions-31/#func-number
    def __init__(self, arguments, qname=None):
        # Returns an xs:QName value formed using a supplied namespace URI and lexical QName.
        super().__init__(arguments, qname, function_name="qname")

    def run(self):
        # Returns an xs:QName value formed using a supplied namespace URI and lexical QName.
        if len(self.cast_args) >= 1:
            # Give back the already casted argument
            return self.cast_args[0]
        else:
            # Otherwise try to cast the argument to float.
            return float(self.arguments[0])


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
