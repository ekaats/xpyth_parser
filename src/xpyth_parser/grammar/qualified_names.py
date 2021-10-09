from typing import Union as typing_Union
from typing import Optional as typing_Optional

from .literals import t_NCName
from ..conversion.qname import qname_from_parse_results, Parameter, QName
from pyparsing import (
    Literal,
    Regex,
    Optional,
    ZeroOrMore,
    Suppress,
)

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
        if variable_name in self.variables.keys():
            return self.variables[variable_name]
        else:
            # return [None]
            raise Exception(f"Variable not in registry: '{variable_name}'")


var_reg = VariableRegistry()

"""
4. Qualified Names
https://www.w3.org/TR/REC-xml-names/#ns-qualnames

"""

t_Prefix = t_NCName
t_Prefix.setName("Prefix")

t_LocalPart = t_NCName
t_LocalPart.setName("LocalPart")

t_PrefixedName = t_Prefix + Suppress(Literal(":")) + t_LocalPart
t_PrefixedName.setName("PrefixedName")

t_UnprefixedName = t_LocalPart
t_UnprefixedName.setName("UnprefixedName")

t_QName = t_PrefixedName | t_UnprefixedName
t_QName.setName("Qname")
t_QName.setParseAction(qname_from_parse_results)

t_BracedURILiteral = (
    Literal("Q") + Literal("{") + ZeroOrMore(Regex("[^{}]")) + Literal("}")
)
t_BracedURILiteral.setName("BracedURILiteral")

t_URIQualifiedName = t_BracedURILiteral + t_NCName
t_URIQualifiedName.setName("URIQualifiedName")
t_EQName = t_QName | t_URIQualifiedName
t_EQName.setName("EQName")

# All these elements refer to QName
t_VarName = t_AtomicType = t_ElementName = t_TypeName = t_AttributeName = t_QName
t_VarName.setName("Varname")

def get_variable(v):


    if len(v) > 1:
        return Parameter(qname=v[0], type_declaration=v[1])
    else:
        var = var_reg.get_variable(v[0])
        # return Parameter(qname=v[0])
        return var

t_VarRef = Suppress(Literal("$")) + t_VarName
t_VarRef.setParseAction(get_variable)
t_VarRef.setName("VarRef")

t_AtomicType.setName("AtomicType")
t_ElementName.setName("ElementName")
t_TypeName.setName("TypeName")
t_AttributeName.setName("AttributeName")

t_SingleType = t_AtomicType + Optional("?")
t_SingleType.setName("SingleType")

# Just as with t_NumericLiteral, the t_Wildcard order needed to be modified slightly
t_Wildcard = (
    (t_NCName + Literal(":") + Literal("*"))
    | (Literal("*") + Literal(":") + t_NCName)
    | Literal("*")
)
t_Wildcard.setName("Wildcard")
