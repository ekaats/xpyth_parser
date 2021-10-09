import functools
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

    def __init__(
            self,
            custom_functions: Optional[dict] = None,
            overwrite_functions: Optional[bool] = False
    ):
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

    def add_functions(self, functions: dict = None, overwrite_functions: Optional[bool] = False):

        if functions is not None:
            for function_name, function in functions.items():
                if function_name not in self.functions.keys():
                    self.functions[function_name] = function
                elif overwrite_functions is True:
                    # Only overwrite functions if this is explicitly set
                    self.functions[function_name] = function


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
