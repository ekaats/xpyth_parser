from pyparsing import (
    Combine,
    Literal,
    Regex,
    MatchFirst,
    Optional,
    OneOrMore,
    Word,
    ZeroOrMore,
    alphas,
    nums,
    srange,
    Forward,
    Keyword, Suppress,
)

from conversion.qname import from_parse_results
from conversion.primaries import str_to_int, str_to_float, str_to_dec

xpath_version = "3.1"

example_test_lines = [
    "not(a)",
    "empty(b)",
    "test()",
    "word",
]


# The following literals are not defined as such in the spec, but we'll define and reuse these to aid readability
# Writing these literals as '(' would be even more readable, but formatting tools such as Black like to change the
# single quotes by double quotes which may change their meaning for pyparsing
l_par_l = Literal("(")
l_par_r = Literal(")")
l_dot = Literal(".")

"""
Primary Expressions
https://www.w3.org/TR/xpath20/#id-primary-expressions
"""

# https://www.w3.org/TR/xpath20/#doc-xpath-IntegerLiteral
t_IntegerLiteral = Word(nums)
t_IntegerLiteral.addParseAction(str_to_int)
t_IntegerLiteral.setName("IntegerLiteral")

t_DecimalLiteral = Combine(l_dot + t_IntegerLiteral) | Combine(
    t_IntegerLiteral + l_dot + Optional(t_IntegerLiteral)
)
t_DecimalLiteral.addParseAction(str_to_float)
t_DecimalLiteral.setName("DecimalLiteral")

# https://www.w3.org/TR/xpath20/#doc-xpath-DoubleLiteral
t_DoubleLiteral = Combine(l_dot + t_IntegerLiteral) | Combine(
    t_IntegerLiteral + Optional(l_dot + Optional(t_IntegerLiteral))
) + (Literal("e") | Literal("E")) + Optional(
    Literal("+") | Literal("-")
) + t_IntegerLiteral
t_DoubleLiteral.addParseAction(str_to_float)
t_DoubleLiteral.setName("DoubleLiteral")

# https://www.w3.org/TR/xpath20/#doc-xpath-NumericLiteral
# Order of the NumericLiteral has been changed compared to spec.
# I think this is necessary for the PEG based PyParsing library to correctly find the type
# https://en.wikipedia.org/wiki/Parsing_expression_grammar
# If IntegerLiteral is checked first, a partial match would be found
t_NumericLiteral = t_DoubleLiteral | t_DecimalLiteral | t_IntegerLiteral
# t_NumericLiteral = t_IntegerLiteral | t_DecimalLiteral | t_DoubleLiteral
t_NumericLiteral.setName("NumericLiteral")


t_EscapeQuot = Literal('""')
t_EscapeQuot.setName("EscapedQuot")
t_EscapeApos = Literal("''")
t_EscapeApos.setName("EscapedApos")
# https://www.w3.org/TR/xpath20/#doc-xpath-StringLiteral
t_StringLiteral = Combine((Suppress('"') + ZeroOrMore(t_EscapeQuot | Regex('[^"]')) + Suppress('"')) | Combine(Suppress("'") + ZeroOrMore(t_EscapeApos | Regex("[^']")) + Suppress("'")))
t_StringLiteral.setName("StringLiteral")

# https://www.w3.org/TR/xpath20/#doc-xpath-Literal
t_Literal = t_NumericLiteral | t_StringLiteral
t_Literal.setName("Literal")

t_Char = Regex(
    "[\u0009\u000a\u000d]|[\u0020-\ud7ff]|[\ue000-\ufffd]|[\U00010000-\U0010ffff]"
)
t_Char.setName("Char")
t_NameStartChar = Regex(
    "[A-Z_a-z\xC0-\xD6\xD8-\xF6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD]"
)
t_NameStartChar.setName("NameStartChar")

# Cannot get the regex mix to work by just passing the Regex() objects to Name,
# so here is a combination of t_nameStartChar and the allowed body chars
t_namechar_regex = (
    "[A-Z_a-z0-9\xC0-\xD6\xD8-\xF6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F"
    "\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\xB7\u0300-\u036F\u203F-\u2040]"
)
t_NameChar = t_NameStartChar | Regex("[-.0-9\xB7\u0300-\u036F\u203F-\u2040]")
t_NameChar.setName("NameChar")


t_Name = Word(
    initChars=srange(t_NameStartChar.pattern), bodyChars=srange(t_namechar_regex)
)
t_Name.setName("Name")
# https://www.w3.org/TR/REC-xml-names/#NT-NCName
t_NCName = t_Name
t_NCName.setName("NCName")
"""
4. Qualified Names
https://www.w3.org/TR/REC-xml-names/#ns-qualnames

"""

t_Prefix = t_NCName
t_Prefix.setName("Prefix")
t_LocalPart = t_NCName
t_LocalPart.setName("LocalPart")
t_PrefixedName = t_Prefix + Suppress(Literal(":")) + t_LocalPart
# t_PrefixedName.addParseAction(from_parse_results)
t_PrefixedName.setName("PrefixedName")

t_UnprefixedName = t_LocalPart
# t_UnprefixedName.addParseAction(from_unprefixed_string)
t_UnprefixedName.setName("UnprefixedName")

t_QName = t_PrefixedName | t_UnprefixedName
t_QName.setName("Qname")
t_QName.setParseAction(from_parse_results)

t_BracedURILiteral = Literal("Q") + Literal("{") + ZeroOrMore(Regex("[^{}]")) + Literal("}")
t_BracedURILiteral.setName("BracedURILiteral")

t_URIQualifiedName = t_BracedURILiteral + t_NCName
t_URIQualifiedName.setName("URIQualifiedName")
t_EQName = t_QName | t_URIQualifiedName
t_EQName.setName("EQName")

# All these elements refer to QName
t_VarName = (
    t_VarRef
) = t_AtomicType = t_ElementName = t_TypeName = t_AttributeName = t_QName
t_VarName.setName("Varname")
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

"""
3. Expressions
https://www.w3.org/TR/xpath20/#id-expressions
"""

# Seems to me that an expression single might actually be basically anything
# Yet, the specs say it should be a ForExpr, IfExpr, etc. But this creates recursion
t_ExprSingle = (
    Forward()
)  # Declare an empty token, as it is used in a recursive declaration later on
t_ExprSingle.setName("ExprSingle")
# SimpleForClause seems to make a lot more sense in the 3.1 spec than in 2.0.
# 2.0:      SimpleForClause 	   ::=    	"for" "$" VarName "in" ExprSingle ("," "$" VarName "in" ExprSingle)*
# 3.1:      SimpleForClause 	   ::=    	"for" SimpleForBinding ("," SimpleForBinding)*
#        	SimpleForBinding 	   ::=    	"$" VarName "in" ExprSingle
t_SimpleForBinding = Literal("$") + t_VarName + Keyword("in") + t_ExprSingle
t_SimpleForBinding.setName("SimpleForBinding")
t_SimpleForClause = (
    Keyword("for") + t_SimpleForBinding + Optional(Literal(",") + t_SimpleForBinding)
)
t_SimpleForClause.setName("SimpleForClause")

t_ForExpr = t_SimpleForClause + Keyword("return") + t_ExprSingle
t_ForExpr.setName("ForExpr")
t_QuantifiedExpr = OneOrMore(
    Keyword("some")
    | Keyword("every")
    + Literal("$")
    + t_VarName
    + Keyword("in")
    + t_ExprSingle
    + ZeroOrMore(Literal(",") + Literal("$") + t_VarName + Keyword("in") + t_ExprSingle)
    + Keyword("satisfies")
    + t_ExprSingle
)
t_QuantifiedExpr.setName("QuantifiedExpr")

t_Expr = t_ExprSingle + ZeroOrMore(Literal(","), t_ExprSingle)
t_Expr.setName("Expr")
# https://www.w3.org/TR/xpath20/#doc-xpath-ParenthesizedExpr
t_ParenthesizedExpr = l_par_l + Optional(t_Expr) + l_par_r
t_ParenthesizedExpr.setName("ParenthesizedExpr")

# https://www.w3.org/TR/xpath20/#doc-xpath-ContextItemExpr
t_ContextItemExpr = l_dot
t_ContextItemExpr.setName("ContextItemExpr")

# XPath 2.0 seems to be less verbose
# https://www.w3.org/TR/xpath-3/#prod-xpath31-FunctionCall
# t_FunctionCall = (
#     t_QName + l_par_l + Optional(t_ExprSingle + ZeroOrMore(Literal(",") + t_ExprSingle)) + l_par_r)
# )
t_ArgumentPlaceholder = Literal("?")
t_ArgumentPlaceholder.setName("ArgumentPlaceholder")
t_Argument = t_ExprSingle | t_ArgumentPlaceholder
t_Argument.setName("Argument")
t_ArgumentList = l_par_l + t_Argument + Optional(ZeroOrMore(Literal(",") + t_Argument)) + l_par_r
t_ArgumentList.setName("ArgumentList")
t_FunctionCall = t_EQName + t_ArgumentList
t_FunctionCall.setName("FunctionCall")

t_IfExpr = (
    Literal("if")
    + l_par_l
    + t_Expr
    + l_par_r
    + Literal("then")
    + t_ExprSingle
    + Literal("else")
    + t_ExprSingle
)
t_IfExpr.setName("IfExpr")
t_PrimaryExpr = (
     t_FunctionCall | t_ParenthesizedExpr | t_VarRef | t_Literal | t_ContextItemExpr
)
t_PrimaryExpr.setName("PrimaryExpr")
t_Predicate = "[" + t_Expr + "]"
t_Predicate.setName("Predicate")

t_PredicateList = ZeroOrMore(t_Predicate)
t_PredicateList.setName("PredicateList")


l_Forward_keywords = Literal("child") | Literal("self") | Literal("descendant-or-self") | Literal("following-sibling") | \
                     Literal("following") | Literal("attribute") | Literal("namespace") | Literal("descendant")
t_ForwardAxis = l_Forward_keywords + Literal("::")
t_ForwardAxis.setName("ForwardAxis")

l_Reverse_keywords =  Literal("preceding-sibling") | Literal("preceding") | Literal("ancestor-or-self") \
                      | Literal("parent") | Literal("ancestor")
t_ReverseAxis = l_Reverse_keywords + Literal("::")
t_ReverseAxis.setName("ReverseAxis")

t_ElementNameOrWildcard = t_ElementName | Literal("*")
t_ElementNameOrWildcard.setName("ElementNameOrWildcard")

"""
TESTS
https://www.w3.org/TR/xpath20/#prod-xpath-KindTest
"""

t_ElementTest = (
    Keyword("element")
    + l_par_l
    + Optional(t_ElementNameOrWildcard + Optional("," + t_TypeName + Optional("?")))
    + l_par_r
)
t_ElementTest.setName("ElementTest")

t_ElementDeclaration = t_ElementName
t_SchemaElementTest = Word("schema-element") + l_par_l + t_ElementDeclaration + l_par_r


t_DocumentTest = (
    Word("document-node")
    + l_par_l
    + Optional(t_ElementTest | t_SchemaElementTest)
    + l_par_r
)
t_DocumentTest.setName("DocumentTest")

t_AttribNameOrWildcard = t_AttributeName | "*"
t_AttribNameOrWildcard.setName("AttribNameOrWildcard")
t_AttributeTest = (
    Word("attribute")
    + l_par_l
    + Optional(t_AttribNameOrWildcard + Optional("," + t_TypeName))
    + l_par_r
)
t_AttributeTest.setName("AttributeTest")

t_AttributeDeclaration = t_AttributeName
t_AttributeDeclaration.setName("AttributeDeclaration")
t_SchemaAttributeTest = Word("schema-attribute") + l_par_l + t_AttributeDeclaration + l_par_r
t_SchemaAttributeTest.setName("SchemaAttributeTest")

t_CommentTest = Word("comment") + l_par_l + l_par_r
t_TextTest = Word("text") + l_par_l + l_par_r
t_AnyKindTest = Word("node") + l_par_l + l_par_r
t_PITest = (
    Word("processing-instruction") + l_par_l + Optional(t_NCName | t_StringLiteral) + l_par_r
)
t_KindTest = (
    t_DocumentTest
    | t_ElementTest
    | t_AttributeTest
    | t_SchemaElementTest
    | t_SchemaAttributeTest
    | t_PITest
    | t_CommentTest
    | t_TextTest
    | t_AnyKindTest
)
t_KindTest.setName("KindTest")

t_NameTest = t_QName | t_Wildcard
t_NameTest.setName("NameTest")

t_NodeTest = t_KindTest | t_NameTest
t_NodeTest.setName("NodeTest")

t_AbbrevForwardStep = Optional("@") + t_NodeTest
t_AbbrevForwardStep.setName("AbbrevForwardStep")

t_AbbrevReverseStep = Word("..")
t_AbbrevReverseStep.setName("AbbrevReverseStep")

t_ForwardStep = (t_ForwardAxis + t_NodeTest) | t_AbbrevForwardStep
t_ForwardStep.setName("ForwardStep")

t_ReverseStep = (t_ReverseAxis + t_NodeTest) | t_AbbrevReverseStep
t_ReverseStep.setName("ReverseStep")

t_AxisStep = (t_ReverseStep | t_ForwardStep) + t_PredicateList
t_AxisStep.setName("AxisStep")

if xpath_version == "2.0":
    t_FilterExpr = t_PrimaryExpr + t_PredicateList
    t_FilterExpr.setName("FilterExpr")

    t_StepExpr = MatchFirst(t_FilterExpr, t_AxisStep)

elif xpath_version == "3.1":
    t_KeySpecifier = t_NCName | t_IntegerLiteral | t_ParenthesizedExpr | Literal("*")
    t_lookup = Literal("?") + t_KeySpecifier
    t_PostfixExpr = t_PrimaryExpr + ZeroOrMore(t_Predicate | t_ArgumentList | t_lookup)
    t_StepExpr = t_PostfixExpr | t_AxisStep


t_RelativePathExpr = t_StepExpr + ZeroOrMore((Literal("/") | Literal("//")) + t_StepExpr)
t_PathExpr = (
                 (Literal("/") + Optional(t_RelativePathExpr))
                 | (Literal("//") + t_RelativePathExpr)
                 | t_RelativePathExpr
)
t_SimpleMapExpr = t_PathExpr + ZeroOrMore(Literal("!") + t_PathExpr)

if xpath_version == "2.0":
    t_ValueExpr = t_PathExpr
elif xpath_version == "3.1":
    t_ValueExpr = t_SimpleMapExpr

t_UnaryExpr = ZeroOrMore(Literal("-") | Literal("+")) + t_ValueExpr
t_UnaryExpr.setName("UnaryExpr")

if xpath_version == "2.0":
    t_CastExpr = t_UnaryExpr + Optional("cast" + "as" + t_SingleType)
elif xpath_version == "3.1":

    t_ArrowFunctionSpecifier = t_EQName | t_VarRef | t_ParenthesizedExpr
    t_ArrowExpr = t_UnaryExpr + ZeroOrMore(Literal("=>") + t_ArrowFunctionSpecifier)
    t_CastExpr = t_ArrowExpr + Optional("cast" + "as" + t_SingleType)



t_CastableExpr = t_CastExpr + Optional("castable" + "as" + t_SingleType)

t_ItemType = t_KindTest | Combine("item" + l_par_l + l_par_r) | t_AtomicType

t_OccurrenceIndicator = Literal("?") | Literal("*") | Literal("+")

t_SequenceType = MatchFirst(
    ("empty-sequence" + l_par_l + l_par_r), (t_ItemType + Optional(t_OccurrenceIndicator))
)

t_TreatExpr = t_CastableExpr + Optional("treat" + "as" + t_SequenceType)
t_InstanceofExpr = t_TreatExpr + MatchFirst("instance" + "of" + t_SequenceType)

t_IntersectExceptExpr = t_InstanceofExpr + ZeroOrMore(
    MatchFirst("intersect", "except") + t_InstanceofExpr
)
t_IntersectExceptExpr.setName("IntersectExceptExpr")

t_UnionExpr = t_IntersectExceptExpr + ZeroOrMore(
    MatchFirst(Word("union") | Literal("|")) + t_IntersectExceptExpr
)
t_UnionExpr.setName("UnionExpr")

t_MultiplicativeExpr = t_UnionExpr + ZeroOrMore(
    MatchFirst(Keyword("*") | Literal("div") | Literal("idiv") | Literal("mod")) + t_UnionExpr
)
t_MultiplicativeExpr.setName("MultiplicativeExpr")

t_AdditiveExpr = t_MultiplicativeExpr + ZeroOrMore(
    MatchFirst(Keyword("+") | Literal("-")) + t_MultiplicativeExpr
)
t_AdditiveExpr.setName("Additive_Expr")

t_RangeExpr = t_AdditiveExpr + Optional(Keyword("to") + t_AdditiveExpr)
t_RangeExpr.setName("RangeExpr")

t_StringConcatExpr = t_RangeExpr + ZeroOrMore(Word("||") + t_AdditiveExpr)
t_StringConcatExpr.setName("StringConcatExpr")

t_ValueComp = (
    Word("eq") | Word("ne") | Word("lt") | Word("le") | Word("gt") | Word("ge")
)
t_GeneralComp = (
    Literal("=") | Word("!=") | Literal("<") | Word("<=") | Literal(">") | Word(">=")
)
t_NodeComp = Word("is") | Word("<<") | Word(">>")
t_ComparisonExpr = t_StringConcatExpr + Optional((t_ValueComp | t_GeneralComp | t_NodeComp) + t_StringConcatExpr)


t_AndExpr = t_ComparisonExpr + ZeroOrMore(Keyword("and") + t_ComparisonExpr)

t_OrExpr = t_AndExpr + ZeroOrMore(Keyword("or") + t_AndExpr)

# Set ExprSingle with actual expressions
t_ExprSingle <<= t_ForExpr | t_QuantifiedExpr | t_IfExpr | t_OrExpr | t_PrimaryExpr
# t_ExprSingle <<= t_ForExpr | t_QuantifiedExpr | t_IfExpr | t_OrExpr


t_XPath = t_Expr
t_XPath.setName("XPath")