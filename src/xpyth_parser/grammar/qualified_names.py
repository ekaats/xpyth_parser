from pyparsing import (
    Literal,
    Regex,
    Optional,
    ZeroOrMore,
    Suppress,
)

from .literals import t_NCName
from ..conversion.qname import qname_from_parse_results, get_variable

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
