from typing import Optional as typing_Optional

from ..conversion.qname import QName

class VariableRegistry:
    _instance = None
    variables = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self,
            variables: typing_Optional[dict] = None,
    ):
        """
        Initialise the VariableRegistry. In this singleton we keep track of all available functions.
        They are used by wrapping into the Function class.

        :param custom_variables:
        """

        if variables is not None:
            for variable_name, variable in variables.items():
                if variable_name not in self.variables.keys():
                    self.variables[variable_name] = variable

    def get_variable(self, variable_name):

        if isinstance(variable_name, QName):
            variable_name = variable_name.__repr__()
        else:
            variable_name = variable_name

        if variable_name in self.variables.keys():
            values = self.variables[variable_name]
            if isinstance(values, list):
                return values
            else:
                return [values]
        else:
            # return [None]
            raise Exception(f"Variable not in registry: '{variable_name}'")














