import ast
import operator

from pyparsing import (
    Combine,
    Literal,
    MatchFirst,
    Optional,
    OneOrMore,
    ZeroOrMore,
    Forward,
    Keyword,
    Word, Suppress,
)


from .literals import l_par_l, l_par_r, l_dot, t_NCName, t_IntegerLiteral, t_Literal

from .qualified_names import t_VarName, t_SingleType, t_AtomicType, t_EQName, t_VarRef
from .tests import t_KindTest, t_NodeTest
from ..conversion.calculation import get_ast, get_unary_expr, get_comparitive_expr
from ..conversion.function import get_function

xpath_version = "3.1"

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


# https://www.w3.org/TR/xpath20/#doc-xpath-ContextItemExpr
t_ContextItemExpr = l_dot
t_ContextItemExpr.setName("ContextItemExpr")



l_Forward_keywords = Literal("child") | Literal("self") | Literal("descendant-or-self") | Literal("following-sibling") | \
                     Literal("following") | Literal("attribute") | Literal("namespace") | Literal("descendant")
t_ForwardAxis = l_Forward_keywords + Literal("::")
t_ForwardAxis.setName("ForwardAxis")

l_Reverse_keywords =  Literal("preceding-sibling") | Literal("preceding") | Literal("ancestor-or-self") \
                      | Literal("parent") | Literal("ancestor")
t_ReverseAxis = l_Reverse_keywords + Literal("::")
t_ReverseAxis.setName("ReverseAxis")


t_AbbrevForwardStep = Optional("@") + t_NodeTest
t_AbbrevForwardStep.setName("AbbrevForwardStep")

t_AbbrevReverseStep = Word("..")
t_AbbrevReverseStep.setName("AbbrevReverseStep")

t_ForwardStep = (t_ForwardAxis + t_NodeTest) | t_AbbrevForwardStep
t_ForwardStep.setName("ForwardStep")

t_ReverseStep = (t_ReverseAxis + t_NodeTest) | t_AbbrevReverseStep
t_ReverseStep.setName("ReverseStep")

t_Predicate = Suppress("[") + t_Expr + Suppress("]")
t_Predicate.setName("Predicate")

t_PredicateList = ZeroOrMore(t_Predicate)
t_PredicateList.setName("PredicateList")

t_AxisStep = (t_ReverseStep | t_ForwardStep) + t_PredicateList
t_AxisStep.setName("AxisStep")

""" Static Function Calls """
t_ArgumentPlaceholder = Literal("?")
t_ArgumentPlaceholder.setName("ArgumentPlaceholder")
t_Argument = t_ExprSingle | t_ArgumentPlaceholder
t_Argument.setName("Argument")
t_ArgumentList = l_par_l + t_Argument + Optional(ZeroOrMore(Suppress(Literal(",")) + t_Argument)) + l_par_r
t_ArgumentList.setName("ArgumentList")

tx_FunctionName = t_EQName

t_FunctionCall = tx_FunctionName + t_ArgumentList

t_FunctionCall.setName("FunctionCall")
t_FunctionCall.setParseAction(get_function)

""" end Static Function Calls """

""" Parentisized Expressions """
t_ParenthesizedExpr = l_par_l + Optional(t_Expr) + l_par_r
t_ParenthesizedExpr.setName("ParenthesizedExpr")

""" end Parentisized Expressions  """


t_PrimaryExpr = t_FunctionCall | t_ParenthesizedExpr | t_Literal | t_VarRef | t_ContextItemExpr

t_PrimaryExpr.setName("PrimaryExpr")


if xpath_version == "2.0":
    t_FilterExpr = t_PrimaryExpr + t_PredicateList
    t_FilterExpr.setName("FilterExpr")

    t_StepExpr = MatchFirst(t_FilterExpr, t_AxisStep)
    t_StepExpr.setName("StepExpr")

elif xpath_version == "3.1":
    t_KeySpecifier = t_NCName | t_IntegerLiteral | t_ParenthesizedExpr | Literal("*")
    t_KeySpecifier.setName("KeySpecifier")

    t_Lookup = Literal("?") + t_KeySpecifier
    t_Lookup.setName("Lookup")

    t_PostfixExpr = t_PrimaryExpr + ZeroOrMore(t_Predicate | t_ArgumentList | t_Lookup)
    t_PostfixExpr.setName("PostfixExpr")

    t_StepExpr = t_PostfixExpr | t_AxisStep
    t_StepExpr.setName("StepExpr")

t_RelativePathExpr = t_StepExpr + ZeroOrMore((Literal("/") | Literal("//")) + t_StepExpr)
t_RelativePathExpr.setName("RelateivePathExpr")

t_PathExpr = (
                 (Literal("/") + Optional(t_RelativePathExpr))
                 | (Literal("//") + t_RelativePathExpr)
                 | t_RelativePathExpr
)
t_PathExpr.setName("PathExpr")



""" Primary Expressions"""

t_NamedFunctionRef = t_EQName + Literal("#") + t_IntegerLiteral
t_NamedFunctionRef.setName("NamedFunctionRef")

t_ItemType = t_KindTest | Combine("item" + l_par_l + l_par_r) | t_AtomicType
t_ItemType.setName("ItemType")

t_OccurrenceIndicator = Literal("?") | Literal("*") | Literal("+")
t_OccurrenceIndicator.setName("OccurenceIndicator")

t_SequenceType = MatchFirst(
    ("empty-sequence" + l_par_l + l_par_r), (t_ItemType + Optional(t_OccurrenceIndicator))
)
t_SequenceType.setName("SequenceType")

t_TypeDeclaration = Literal("as") + t_SequenceType
t_TypeDeclaration.setName("TypeDeclaration")

t_Param = Literal("$") + t_EQName + Optional(t_TypeDeclaration)
t_Param.setName("Param")

t_ParamList = t_Param + ZeroOrMore(Literal(","), t_Param)
t_ParamList.setName("ParamList")

t_InlineFunctionExpr = Keyword("function") + l_par_l + Optional(t_ParamList) + l_par_r + Optional(Keyword("as") + t_SequenceType)
t_InlineFunctionExpr.setName("InlineFunctionExpr")

t_FunctionItemExpr = t_NamedFunctionRef | t_InlineFunctionExpr
t_FunctionItemExpr.setName("FunctionItemExpr")

t_MapKeyExpr = t_MapValueExpr = t_ExprSingle
t_MapKeyExpr.setName("MapKeyExpr")

t_MapConstructorEntry = t_MapKeyExpr + Literal(":") + t_MapValueExpr
t_MapConstructorEntry.setName("MapConstructorEntry")

t_MapConstructor = Literal("map") + Literal("{") + Optional(t_MapConstructorEntry, ZeroOrMore(Literal(",") + t_MapConstructorEntry))
t_MapConstructor.setName("MapConstructor")

t_SquareArrayConstructor = Literal("[") + Optional(l_par_l + t_ExprSingle + ZeroOrMore(Literal(",") + t_ExprSingle)) + Literal("]")

t_EnclosedExpr = Literal("{") + Optional(t_Expr) + Literal("}")
t_EnclosedExpr.setName("EnclosedExpr")

t_CurlyArrayConstructor = Keyword("array") + t_EnclosedExpr
t_CurlyArrayConstructor.setName("CurlyArrayConstructor")

t_ArrayConstructor = t_SquareArrayConstructor | t_CurlyArrayConstructor
t_ArrayConstructor.setName("ArrayConstructor")

t_UnaryLookup = Literal("?") + t_KeySpecifier



""" end Primary Expressions"""

"""Comparison Expressions"""
if xpath_version == "2.0":
    t_ValueExpr = t_PathExpr
    t_ValueExpr.setName("ValueExpr")
elif xpath_version == "3.1":

    t_SimpleMapExpr = t_PathExpr + ZeroOrMore(Literal("!") + t_PathExpr)
    t_SimpleMapExpr.setName("SimpleMapExpr")

    t_ValueExpr = t_SimpleMapExpr
    t_ValueExpr.setName("ValueExpr")
""" end Comparison Expressions """


""" Sequence Types """

# Subtractor needs to be preceded with a whitespace, but is allowed to be succeeded with non-whitespace
# https://www.w3.org/TR/xpath-3/#id-arithmetic
t_UnaryExpr = ZeroOrMore(Literal(" -") | Literal("+")) + t_ValueExpr

t_UnaryExpr.setName("UnaryExpr")
t_UnaryExpr.setParseAction(get_unary_expr)


if xpath_version == "2.0":
    t_CastExpr = t_UnaryExpr + Optional(Keyword("cast") + Keyword("as") + t_SingleType)
elif xpath_version == "3.1":

    t_ArrowFunctionSpecifier = t_EQName | t_VarRef | t_ParenthesizedExpr
    t_ArrowExpr = t_UnaryExpr + ZeroOrMore(Literal("=>") + t_ArrowFunctionSpecifier)
    t_CastExpr = t_ArrowExpr + Optional(Keyword("cast") + Keyword("as") + t_SingleType)



t_CastableExpr = t_CastExpr + Optional(Keyword("castable") + Keyword("as") + t_SingleType)


t_TreatExpr = t_CastableExpr + Optional(Keyword("treat") + Keyword("as") + t_SequenceType)
t_TreatExpr.setName("TreatExpr")

t_InstanceofExpr = t_TreatExpr + Optional(Keyword("instance") + Keyword("of") + t_SequenceType)
t_InstanceofExpr.setName("InstanceofExpr")

""" end Sequence Types"""


"""Combining node sequences"""

t_IntersectExceptExpr = t_InstanceofExpr + ZeroOrMore(
    MatchFirst(Keyword("intersect"), Keyword("except")) + t_InstanceofExpr
)
t_IntersectExceptExpr.setName("IntersectExceptExpr")

t_UnionExpr = t_IntersectExceptExpr + ZeroOrMore(
    MatchFirst(Word("union") | Literal("|")) + t_IntersectExceptExpr
)
t_UnionExpr.setName("UnionExpr")
"""end Combining node sequences"""


""" Arithmetic Expressions """

tx_ArithmeticMultiplicativeSymbol = Literal("*") | Keyword("div") | Keyword("idiv") | Keyword("mod")

t_ArithmeticAdditiveSymbol = Literal("+") | Literal("-")

tx_MultiplicativeExpr = t_UnionExpr + ZeroOrMore(tx_ArithmeticMultiplicativeSymbol + t_UnionExpr)

tx_MultiplicativeExpr.setName("MultiplicativeExpr")

t_AdditiveExpr = tx_MultiplicativeExpr + ZeroOrMore(t_ArithmeticAdditiveSymbol + tx_MultiplicativeExpr)
t_AdditiveExpr.setParseAction(get_ast)
t_AdditiveExpr.setName("Additive_Expr")


t_RangeExpr = t_AdditiveExpr + Optional(Keyword("to") + t_AdditiveExpr)
t_RangeExpr.setName("RangeExpr")

""" end Arithmetic Expressions"""


""" Comparison expressions """

t_ValueComp = (
    Keyword("eq") | Keyword("ne") | Keyword("lt") | Keyword("le") | Keyword("gt") | Keyword("ge")
)
t_ValueComp.setName("ValueComp")

# Todo: Cast GeneralComp in to pythonic operators. Could we use the same as for ValueComp?
t_GeneralComp = (
    Keyword("=") | Keyword("!=") | Keyword("<") | Keyword("<=") | Keyword(">") | Keyword(">=")
)
t_GeneralComp.setName("GeneralComp")


t_NodeComp = Word("is") | Word("<<") | Word(">>")
t_NodeComp.setName("NodeComp")

if xpath_version == "2.0":
    t_ComparisonExpr = t_RangeExpr + Optional((t_ValueComp | t_GeneralComp | t_NodeComp) + t_RangeExpr)
    t_ComparisonExpr.setName("ComparisonExpr")
    t_ComparisonExpr.setParseAction(get_comparitive_expr)

elif xpath_version == "3.1":
    t_StringConcatExpr = t_RangeExpr + ZeroOrMore(Word("||") + t_AdditiveExpr)
    t_StringConcatExpr.setName("StringConcatExpr")

    t_ComparisonExpr = t_StringConcatExpr + Optional((t_ValueComp | t_GeneralComp | t_NodeComp) + t_StringConcatExpr)
    t_ComparisonExpr.setName("ComparisonExpr")
    t_ComparisonExpr.setParseAction(get_comparitive_expr)


""" end Comparison expresisons"""


""" Logical Expressions """
t_AndExpr = t_ComparisonExpr + ZeroOrMore(Keyword("and") + t_ComparisonExpr)
t_AndExpr.setName("AndExpr")


t_OrExpr = t_AndExpr + ZeroOrMore(Keyword("or") + t_AndExpr)
t_OrExpr.setName("OrExpr")

""" end Logical Expressions """


""" Conditional Expression """
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
""" end Conditional Expression """

t_SimpleLetBinding = Literal("$") + t_VarName + Keyword(":=") + t_ExprSingle
t_SimpleLetBinding.setName("SimpleLetBinding")
t_SimpleLetClause = Keyword("let") + t_SimpleLetBinding + ZeroOrMore(Literal(",") + t_SimpleLetBinding)
t_SimpleLetClause.setName("SimpleLetClause")

t_LetExpr = t_SimpleLetClause + Keyword("return") + t_ExprSingle
t_LetExpr.setName("LetExpr")

# Set ExprSingle with actual expressions
t_ExprSingle <<= t_ForExpr | t_OrExpr | t_QuantifiedExpr | t_IfExpr | t_LetExpr

t_XPath = t_Expr
t_XPath.setName("XPath")

# todo: Generating a railroad map requires Pyparsing 3.0. Uncomment when PP3.0 is released from beta
# def create_railroad():
#     from pyparsing.diagram import to_railroad, railroad_to_html
#
#     with open('/tmp/output.html', 'w') as fp:
#         railroad = to_railroad(t_Expr)
#         fp.write(railroad_to_html(railroad))

