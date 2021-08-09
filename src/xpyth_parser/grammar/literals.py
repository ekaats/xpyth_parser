import ast

from pyparsing import (
    Combine,
    Literal,
    Regex,
    Optional,
    Word,
    ZeroOrMore,
    nums,
    srange,
    Suppress,
)

from ..conversion.primaries import str_to_int, str_to_float

xpath_version = "3.1"

# The following literals are not defined as such in the spec, but we'll define and reuse these to aid readability
# Writing these literals as '(' would be even more readable, but formatting tools such as Black like to change the
# single quotes by double quotes which may change their meaning for pyparsing
l_par_l = Suppress(Literal("("))
l_par_r = Suppress(Literal(")"))
l_dot = Literal(".")

"""
Primary Expressions
https://www.w3.org/TR/xpath20/#id-primary-expressions
"""

# https://www.w3.org/TR/xpath20/#doc-xpath-IntegerLiteral
t_IntegerLiteral = Word(nums)
t_IntegerLiteral.addParseAction(str_to_int)

t_DecimalLiteral = Combine(l_dot + t_IntegerLiteral) | Combine(
    t_IntegerLiteral + l_dot + Optional(t_IntegerLiteral)
)
t_DecimalLiteral.addParseAction(str_to_float)

# https://www.w3.org/TR/xpath20/#doc-xpath-DoubleLiteral
t_DoubleLiteral = (
    Combine(l_dot + t_IntegerLiteral)
    | Combine(t_IntegerLiteral + Optional(l_dot + Optional(t_IntegerLiteral)))
    + (Literal("e") | Literal("E"))
    + Optional(Literal("+") | Literal("-"))
    + t_IntegerLiteral
)
t_DoubleLiteral.addParseAction(str_to_float)

# https://www.w3.org/TR/xpath20/#doc-xpath-NumericLiteral
# Order of the NumericLiteral has been changed compared to spec.
# I think this is necessary for the PEG based PyParsing library to correctly find the type
# https://en.wikipedia.org/wiki/Parsing_expression_grammar


def get_numeric_literal_ast(v):
    # unparsed_num = v[0]

    ast_num = ast.Constant(v[0])
    return ast_num


# If IntegerLiteral is checked first, a partial match would be found
t_NumericLiteral = t_DoubleLiteral | t_DecimalLiteral | t_IntegerLiteral
t_NumericLiteral.setName("NumericLiteral")
t_NumericLiteral.setParseAction(get_numeric_literal_ast)


t_EscapeQuot = Literal('""')
t_EscapeQuot.setName("EscapedQuot")
t_EscapeApos = Literal("''")
t_EscapeApos.setName("EscapedApos")
# https://www.w3.org/TR/xpath20/#doc-xpath-StringLiteral
t_StringLiteral = Combine(
    (Suppress('"') + ZeroOrMore(t_EscapeQuot | Regex('[^"]')) + Suppress('"'))
    | Combine(Suppress("'") + ZeroOrMore(t_EscapeApos | Regex("[^']")) + Suppress("'"))
)
t_StringLiteral.setName("StringLiteral")

# https://www.w3.org/TR/xpath20/#doc-xpath-Literal
t_Literal = t_NumericLiteral | t_StringLiteral
t_Literal.setName("Literal")


def catch_literal(v):
    v_l = list(v)
    return v


t_Literal.setParseAction(catch_literal)

t_Char = Regex(
    "[\u0009\u000a\u000d]|[\u0020-\ud7ff]|[\ue000-\ufffd]|[\U00010000-\U0010ffff]"
)
t_Char.setName("Char")
s_NameStartCharRegex = "A-Z_a-z\xC0-\xD6\xD8-\xF6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD"
t_NameStartChar = Regex(f"[{s_NameStartCharRegex}]")
t_NameStartChar.setName("NameStartChar")

# Cannot get the regex mix to work by just passing the Regex() objects to Name,
# so here is a combination of t_nameStartChar and the allowed body chars
# t_namechar_regex = (
#     "A-Z_a-z0-9\xC0-\xD6\xD8-\xF6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F"
#     "\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\xB7\u0300-\u036F\u203F-\u2040"
# )
s_NameCharRegex = f"[-.0-9\xB7{s_NameStartCharRegex}\u0300-\u036F\u203F-\u2040]"

t_NameChar = Regex(s_NameCharRegex)
t_NameChar.setName("NameChar")


t_Name = Word(
    initChars=srange(t_NameStartChar.pattern), bodyChars=srange(t_NameChar.pattern)
)
t_Name.setName("Name")
# https://www.w3.org/TR/REC-xml-names/#NT-NCName
t_NCName = t_Name
t_NCName.setName("NCName")
