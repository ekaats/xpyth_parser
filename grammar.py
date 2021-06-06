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
    Keyword,
)


example_test_lines = [
    "not(a)",
    "empty(b)",
    "test()",
    "word",
    "$varArc_BalanceSheet_PrtFST1SumOfChildrenDParentDebit3_Assets = - sum($varArc_BalanceSheet_PrtFST1SumOfChildrenDParentDebit3_ChildrenOfAssetsCredit)+ sum($varArc_BalanceSheet_PrtFST1SumOfChildrenDParentDebit3_ChildrenOfAssetsDebit)",
]


# Define XPath 2.0 tokens

"""
Primary Expressions
https://www.w3.org/TR/xpath20/#id-primary-expressions
"""


# https://www.w3.org/TR/xpath20/#doc-xpath-IntegerLiteral
t_IntegerLiteral = Word(nums)
t_IntegerLiteral.setName("IntegerLiteral")

# https://www.w3.org/TR/xpath20/#doc-xpath-DecimalLiteral
#  	DecimalLiteral 	   ::=    	("." Digits) | (Digits "." [0-9]*)
t_DecimalLiteral = ("." + t_IntegerLiteral) | (
    t_IntegerLiteral + "." + Optional(t_IntegerLiteral)
)
t_DecimalLiteral.setName("DecimalLiteral")

# https://www.w3.org/TR/xpath20/#doc-xpath-DoubleLiteral
t_DoubleLiteral = (Literal(".") + t_IntegerLiteral) | (
    t_IntegerLiteral + Optional(Literal(".") + Optional(t_IntegerLiteral))
) + (Literal("e") | Literal("E")) + Optional(
    Literal("+") | Literal("-")
) + t_IntegerLiteral
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
t_StringLiteral = Combine((Literal('"') + ZeroOrMore(t_EscapeQuot | Regex('[^"]')) + Literal('"')) | (Literal("'") + ZeroOrMore(t_EscapeApos | Regex("[^']")) + Literal("'")))
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
t_PrefixedName = t_Prefix + ":" + t_LocalPart
t_PrefixedName.setName("PrefixedName")
t_UnprefixedName = t_LocalPart
t_UnprefixedName.setName("UnprefixedName")

t_QName = t_PrefixedName | t_UnprefixedName
t_QName.setName("Qname")
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
t_ParenthesizedExpr = "(" + Optional(t_Expr) + ")"
t_ParenthesizedExpr.setName("ParenthesizedExpr")

# https://www.w3.org/TR/xpath20/#doc-xpath-ContextItemExpr
t_ContextItemExpr = Literal(".")
t_ContextItemExpr.setName("ContextItemExpr")

# XPath 2.0 seems to be less verbose
# https://www.w3.org/TR/xpath-3/#prod-xpath31-FunctionCall
# t_FunctionCall = (
#     t_QName + Literal("(") + Optional(t_ExprSingle + ZeroOrMore(Literal(",") + t_ExprSingle)) + Literal(")")
# )
t_ArgumentPlaceholder = Literal("?")
t_ArgumentPlaceholder.setName("ArgumentPlaceholder")
t_Argument = t_ExprSingle | t_ArgumentPlaceholder
t_Argument.setName("Argument")
t_ArgumentList = Literal("(") + Optional(t_Argument + ZeroOrMore(Literal(",") + t_Argument)) + Literal(")")
t_ArgumentList.setName("ArgumentList")
t_FunctionCall = t_EQName + t_ArgumentList
t_FunctionCall.setName("FunctionCall")

t_IfExpr = (
    Literal("if")
    + Literal("(")
    + t_Expr
    + Literal(")")
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
t_FilterExpr = t_PrimaryExpr + t_PredicateList
t_FilterExpr.setName("FilterExpr")

t_ForwardAxis = (
    Word("child" + "::")
    | Word("descendant" + "::")
    | Word("attribute" + "::")
    | Word("self" + "::")
    | Word("descendant-or-self" + "::")
    | Word("following-sibling" + "::")
    | Word("following" + "::")
    | Word("namespace" + "::")
)
t_ForwardAxis.setName("ForwardAxis")
t_ReverseAxis = (
    Word("parent" + "::")
    | Word("ancestor" + "::")
    | Word("preceding-sibling" + "::")
    | Word("preceding" + "::")
    | Word("ancestor-or-self" + "::")
)
t_ReverseAxis.setName("ReverseAxis")

t_ElementNameOrWildcard = t_ElementName | Literal("*")
t_ElementNameOrWildcard.setName("ElementNameOrWildcard")

"""
TESTS
https://www.w3.org/TR/xpath20/#prod-xpath-KindTest
"""

t_ElementTest = (
    Word("element")
    + "("
    + Optional(t_ElementNameOrWildcard + Optional("," + t_TypeName + Optional("?")))
    + Literal(")")
)

t_ElementDeclaration = t_ElementName
t_SchemaElementTest = Word("schema-element") + "(" + t_ElementDeclaration + ")"


t_DocumentTest = (
    Word("document-node")
    + Literal("(")
    + Optional(t_ElementTest | t_SchemaElementTest)
    + Literal(")")
)

t_AttribNameOrWildcard = t_AttributeName | "*"
t_AttributeTest = (
    Word("attribute")
    + "("
    + Optional(t_AttribNameOrWildcard + Optional("," + t_TypeName))
    + ")"
)

t_AttributeDeclaration = t_AttributeName
t_SchemaAttributeTest = Word("schema-attribute") + "(" + t_AttributeDeclaration + ")"

t_CommentTest = Word("comment") + "(" + ")"
t_TextTest = Word("text") + "(" + ")"
t_AnyKindTest = Word("node") + "(" + ")"
t_PITest = (
    Word("processing-instruction") + "(" + Optional(t_NCName | t_StringLiteral) + ")"
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

t_NameTest = t_QName | t_Wildcard

t_NodeTest = t_KindTest | t_NameTest

t_AbbrevForwardStep = Optional("@") + t_NodeTest
t_AbbrevReverseStep = Word("..")

t_ForwardStep = (t_ForwardAxis + t_NodeTest) | t_AbbrevForwardStep
t_ReverseStep = (t_ReverseAxis + t_NodeTest) | t_AbbrevReverseStep
t_AxisStep = (t_ReverseStep | t_ForwardStep) + t_PredicateList
t_StepExpr = MatchFirst(t_FilterExpr, t_AxisStep)
t_RelativePathExpr = t_StepExpr + (Literal("/") | Literal("//") + t_StepExpr)
t_PathExpr = (
    "/"
    + Optional(t_RelativePathExpr)
    + MatchFirst("//" + t_RelativePathExpr, t_RelativePathExpr)
)

t_ValueExpr = t_PathExpr


t_UnaryExpr = ZeroOrMore("-", "+") + t_ValueExpr

t_CastExpr = t_UnaryExpr + Optional("cast" + "as" + t_SingleType)

t_CastableExpr = t_CastExpr + Optional("castable" + "as" + t_SingleType)

t_ItemType = t_KindTest | Word("item" + "(" + ")") | t_AtomicType

t_OccurrenceIndicator = Literal("?") | Literal("*") | Literal("+")

t_SequenceType = MatchFirst(
    ("empty-sequence" + "(" ")"), (t_ItemType + Optional(t_OccurrenceIndicator))
)

t_TreatExpr = t_CastableExpr + Optional("treat" + "as" + t_SequenceType)
t_InstanceofExpr = t_TreatExpr + MatchFirst("instance" + "of" + t_SequenceType)
t_IntersectExceptExpr = t_InstanceofExpr + ZeroOrMore(
    MatchFirst("intersect", "except") + t_InstanceofExpr
)
t_UnionExpr = t_IntersectExceptExpr + ZeroOrMore(
    MatchFirst(Word("union") | Literal("|")) + t_IntersectExceptExpr
)
t_MultiplicativeExpr = t_UnionExpr + ZeroOrMore(
    MatchFirst(Literal("*") | Word("div") | Word("idiv") | Word("mod")) + t_UnionExpr
)
t_AdditiveExpr = t_MultiplicativeExpr + ZeroOrMore(
    MatchFirst(Literal("+") | Literal("-")) + t_MultiplicativeExpr
)
t_RangeExpr = t_AdditiveExpr + Optional("to" + t_AdditiveExpr)

t_ValueComp = (
    Word("eq") | Word("ne") | Word("lt") | Word("le") | Word("gt") | Word("ge")
)
t_GeneralComp = (
    Literal("=") | Word("!=") | Literal("<") | Word("<=") | Literal(">") | Word(">=")
)
t_NodeComp = Word("is") | Word("<<") | Word(">>")
t_ComparisonExpr = t_RangeExpr + Optional(
    MatchFirst(t_ValueComp | t_GeneralComp | t_NodeComp) + t_RangeExpr
)

t_AndExpr = t_ComparisonExpr + ZeroOrMore("and" + t_ComparisonExpr)

t_OrExpr = t_AndExpr + ZeroOrMore("or" + t_AndExpr)

# Set ExprSingle with actual expressions
t_ExprSingle <<= t_ForExpr | t_QuantifiedExpr | t_IfExpr | t_OrExpr | t_PrimaryExpr
# t_ExprSingle <<= t_ForExpr | t_QuantifiedExpr | t_IfExpr | t_OrExpr


t_XPath = t_Expr
t_XPath.setName("XPath")