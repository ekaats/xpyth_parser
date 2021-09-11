from pyparsing import (
    Combine,
    Literal,
    MatchFirst,
    Optional,
    OneOrMore,
    ZeroOrMore,
    Forward,
    Keyword,
    Suppress,
)


from .literals import l_par_l, l_par_r, l_dot, t_NCName, t_IntegerLiteral, t_Literal

from .qualified_names import t_VarName, t_SingleType, t_AtomicType, t_EQName, t_VarRef
from .tests import t_KindTest, t_NodeTest
from ..conversion.calculation import (
    get_additive_expr,
    get_unary_expr,
    get_comparitive_expr,
    Operator,
    Compare,
    CompareValue,
)
from ..conversion.expressions import IfExpression
from ..conversion.function import get_function
from ..conversion.functions.generic import Function, Datatype
from ..conversion.path import get_single_path_expr, get_path_expr, PathExpression


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


class Expr:

    def resolve_expression(self):
        raise NotImplementedError

class IfExpression(Expr):
    def __init__(self, test_expr, then_expr, else_expr):

        self.test_expr = test_expr
        self.then_expr = then_expr
        self.else_expr = else_expr

    def resolve_expression(self, test_outcome):

        # Then and Else are both SingleExpressions
        if test_outcome is True:
            # Test has succeeded, so we return the 'then' ExprSingle

            return_expr = self.then_expr
        else:

            return_expr = self.else_expr

        return return_expr


def resolve_expression(expression, variable_map, lxml_etree):
    """
    Loops though parsed results and resolves qnames using the variable_map

    :return:
    """
    # Set variable map and lxml etree. These should not be set at this time

    def resolve_fn(fn):
        """
        Wrapper function to run Functions
        :param fn:
        :return:
        """

        fn.resolve_paths(lxml_etree=lxml_etree)
        fn.cast_parameters(paramlist=variable_map)

        # Then get the value by running the function
        value = fn.run()

        # Put the output value of the function into the AST as a number

        return value

    if hasattr(expression, "expr"):
        # Expresssion needs to be unpacked:
        rootexpr = expression.expr
    else:
        rootexpr = expression

    # First try to get the children of the node.
    if hasattr(rootexpr, "process_children"):
        # resolve children of expr
        child_generator = rootexpr.process_children()
        for child in child_generator:
            if isinstance(child, int):
                # No need to resolve further
                pass
            else:
                resolved_child = resolve_expression(
                    expression=child,
                    variable_map=variable_map,
                    lxml_etree=lxml_etree,
                )
                # Return the resolved child back to the generator
                try:
                    child_generator.send(resolved_child)
                except:
                    pass
                    # print("Couldn't give the child back to generator")

    if isinstance(rootexpr, Function):
        # Main node is a Function. Resolve this and add the answer to the AST.
        rootexpr = resolve_fn(rootexpr)

    elif isinstance(rootexpr, Operator):
        rootexpr = rootexpr.answer()

    elif isinstance(rootexpr, Datatype):
        # Syntactically simmilar to a Function, but a datatype should not be wrapped
        pass

    elif isinstance(rootexpr, IfExpression):

        # Replace the if statement with its outcome
        outcome_of_test = resolve_expression(
            expression=rootexpr.test_expr,
            variable_map=variable_map,
            lxml_etree=lxml_etree,
        )
        rootexpr = rootexpr.resolve_expression(test_outcome=outcome_of_test)

    elif isinstance(rootexpr, XPath):
        # Need to recursively run the child

        # Resolve the expression and substitute the expression for the answer
        resolved_expr = resolve_expression(
            expression=rootexpr,
            variable_map=variable_map,
            lxml_etree=lxml_etree,
        )
        rootexpr = resolved_expr

    elif isinstance(rootexpr, PathExpression):
        # Run the path expression against the LXML etree
        resolved_expr = rootexpr.resolve_path(lxml_etree=lxml_etree)
        # if resolved_expr is not None:
        rootexpr = resolved_expr

    elif isinstance(rootexpr, Compare):
        # Pass data into the comparator
        rootexpr.resolve(variable_map=variable_map, lxml_etree=lxml_etree)

        # Get answer
        rootexpr = rootexpr.answer()

    # Give back the now resolved expression
    return rootexpr


class XPath:
    def __init__(self, expr, variable_map=None, xml_etree=None):

        self.expr = expr

        self.variable_map = variable_map if variable_map else {}
        self.lxml_etree = xml_etree

    def resolve_child(self):
        return resolve_expression(
            self.expr, variable_map=self.variable_map, lxml_etree=self.lxml_etree
        )


t_Expr = t_ExprSingle + ZeroOrMore(Literal(","), t_ExprSingle)
t_Expr.setName("Expr")
t_Expr.setParseAction(lambda x: XPath(expr=x[0]))

# https://www.w3.org/TR/xpath20/#doc-xpath-ParenthesizedExpr


# https://www.w3.org/TR/xpath20/#doc-xpath-ContextItemExpr
class ContextItem:
    def __init__(self):
        self.value = None


t_ContextItemExpr = l_dot
t_ContextItemExpr.setName("ContextItemExpr")
t_ContextItemExpr.setParseAction(lambda: ContextItem())


def find_context_item(expression, variable_map, lxml_etree, context_item):
    """
    Attempts to find the context item in the grammar tree

    :param expression:
    :return:
    """

    if hasattr(expression.expr, "process_children"):
        child_generator = expression.expr.process_children()
        for child in child_generator:
            if isinstance(child, ContextItem):
                # The expression has a context item. So we should first resolve this one.

                print("")
                context_expr = XPath(expr=context_item)
                # A Sequence is returned
                #  https://www.w3.org/TR/xpath-3/#id-sequence-expressions
                # A sequence may contain duplicate items, but a sequence is never an item in another sequence.
                # When a new sequence is created by concatenating two or more input sequences,
                # the new sequence contains all the items of the input sequences and its length is the sum of the
                # lengths of the input sequences.

                # This should be expected for every context query

                # todo: Maybe check out how LXML reals with extension functions:
                #  https://lxml.de/extensions.html#xpath-extension-functions
                #  I guess there it actually matters
                #  but also with 'eq' and comparators? Xpath 1.0 only has equality comparators

                child_generator.send(context_expr)

                # todo: it is worse:
                #  https://www.marklogic.com/blog/xpath-punctuation-part-1/

                resolved_expr = expression.expr.resolve(
                    variable_map=variable_map, lxml_etree=lxml_etree
                )
                print("")


l_Forward_keywords = (
    Keyword("child")
    | Keyword("self")
    | Keyword("descendant-or-self")
    | Keyword("following-sibling")
    | Keyword("following")
    | Keyword("attribute")
    | Keyword("namespace")
    | Keyword("descendant")
)
t_ForwardAxis = l_Forward_keywords + Literal("::")
t_ForwardAxis.setName("ForwardAxis")

l_Reverse_keywords = (
    Keyword("preceding-sibling")
    | Keyword("preceding")
    | Keyword("ancestor-or-self")
    | Keyword("parent")
    | Keyword("ancestor")
)
t_ReverseAxis = l_Reverse_keywords + Literal("::")
t_ReverseAxis.setName("ReverseAxis")


t_AbbrevForwardStep = Optional("@") + t_NodeTest
t_AbbrevForwardStep.setName("AbbrevForwardStep")


t_AbbrevReverseStep = Keyword("..")
t_AbbrevReverseStep.setName("AbbrevReverseStep")


t_ForwardStep = (t_ForwardAxis + t_NodeTest) | t_AbbrevForwardStep
t_ForwardStep.setName("ForwardStep")


t_ReverseStep = (t_ReverseAxis + t_NodeTest) | t_AbbrevReverseStep
t_ReverseStep.setName("ReverseStep")

t_Predicate = Suppress("[") + t_Expr + Suppress("]")
t_Predicate.setName("Predicate")


class Predicate:
    def __init__(self, val):
        self.val = val


def predicate(v):
    # print(f"Getting predicate: {v[0]}")
    return Predicate(val=v[0])


t_Predicate.setParseAction(predicate)


def get_predicate_list(toks):
    # Round up all predicates
    predicates = []
    for tok in toks:
        if isinstance(tok, Predicate):
            predicates.append(tok)

    return predicates


t_PredicateList = ZeroOrMore(t_Predicate)
t_PredicateList.setName("PredicateList")
t_PredicateList.setParseAction(get_predicate_list)


t_AxisStep = (t_ReverseStep | t_ForwardStep) + t_PredicateList
t_AxisStep.setName("AxisStep")

""" Static Function Calls """
t_ArgumentPlaceholder = Literal("?")
t_ArgumentPlaceholder.setName("ArgumentPlaceholder")
t_Argument = t_ExprSingle | t_ArgumentPlaceholder
t_Argument.setName("Argument")
t_ArgumentList = (
    l_par_l
    + t_Argument
    + Optional(ZeroOrMore(Suppress(Literal(",")) + t_Argument))
    + l_par_r
)
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


t_PrimaryExpr = (
    t_FunctionCall | t_ParenthesizedExpr | t_Literal | t_VarRef | t_ContextItemExpr
)

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


tx_SinglePathExpr = MatchFirst(Literal("//") | Literal("/")) + t_StepExpr

tx_SinglePathExpr.setParseAction(get_single_path_expr)

t_RelativePathExpr = t_StepExpr + ZeroOrMore(tx_SinglePathExpr)
t_RelativePathExpr.setName("RelativePathExpr")


t_PathExpr = (
    (Literal("//") + t_RelativePathExpr)
    | (Literal("/") + Optional(t_RelativePathExpr))
    | t_RelativePathExpr
)
t_PathExpr.setName("PathExpr")


t_PathExpr.setParseAction(get_path_expr)


""" Primary Expressions"""

t_NamedFunctionRef = t_EQName + Literal("#") + t_IntegerLiteral
t_NamedFunctionRef.setName("NamedFunctionRef")

t_ItemType = t_KindTest | Combine("item" + l_par_l + l_par_r) | t_AtomicType
t_ItemType.setName("ItemType")

t_OccurrenceIndicator = Literal("?") | Literal("*") | Literal("+")
t_OccurrenceIndicator.setName("OccurenceIndicator")

t_SequenceType = MatchFirst(
    ("empty-sequence" + l_par_l + l_par_r),
    (t_ItemType + Optional(t_OccurrenceIndicator)),
)
t_SequenceType.setName("SequenceType")

t_TypeDeclaration = Keyword("as") + t_SequenceType
t_TypeDeclaration.setName("TypeDeclaration")

t_Param = Literal("$") + t_EQName + Optional(t_TypeDeclaration)
t_Param.setName("Param")

t_ParamList = t_Param + ZeroOrMore(Literal(","), t_Param)
t_ParamList.setName("ParamList")

t_InlineFunctionExpr = (
    Keyword("function")
    + l_par_l
    + Optional(t_ParamList)
    + l_par_r
    + Optional(Keyword("as") + t_SequenceType)
)
t_InlineFunctionExpr.setName("InlineFunctionExpr")

t_FunctionItemExpr = t_NamedFunctionRef | t_InlineFunctionExpr
t_FunctionItemExpr.setName("FunctionItemExpr")

t_MapKeyExpr = t_MapValueExpr = t_ExprSingle
t_MapKeyExpr.setName("MapKeyExpr")

t_MapConstructorEntry = t_MapKeyExpr + Literal(":") + t_MapValueExpr
t_MapConstructorEntry.setName("MapConstructorEntry")

t_MapConstructor = (
    Literal("map")
    + Literal("{")
    + Optional(t_MapConstructorEntry, ZeroOrMore(Literal(",") + t_MapConstructorEntry))
)
t_MapConstructor.setName("MapConstructor")

t_SquareArrayConstructor = (
    Literal("[")
    + Optional(l_par_l + t_ExprSingle + ZeroOrMore(Literal(",") + t_ExprSingle))
    + Literal("]")
)


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
t_UnaryExpr = ZeroOrMore(Literal("-") | Literal("+")) + t_ValueExpr

t_UnaryExpr.setName("UnaryExpr")
t_UnaryExpr.setParseAction(get_unary_expr)


if xpath_version == "2.0":
    t_CastExpr = t_UnaryExpr + Optional(Keyword("cast") + Keyword("as") + t_SingleType)
elif xpath_version == "3.1":

    t_ArrowFunctionSpecifier = t_EQName | t_VarRef | t_ParenthesizedExpr
    t_ArrowExpr = t_UnaryExpr + ZeroOrMore(Literal("=>") + t_ArrowFunctionSpecifier)
    t_CastExpr = t_ArrowExpr + Optional(Keyword("cast") + Keyword("as") + t_SingleType)


t_CastableExpr = t_CastExpr + Optional(
    Keyword("castable") + Keyword("as") + t_SingleType
)


t_TreatExpr = t_CastableExpr + Optional(
    Keyword("treat") + Keyword("as") + t_SequenceType
)
t_TreatExpr.setName("TreatExpr")

t_InstanceofExpr = t_TreatExpr + Optional(
    Keyword("instance") + Keyword("of") + t_SequenceType
)
t_InstanceofExpr.setName("InstanceofExpr")

""" end Sequence Types"""


"""Combining node sequences"""

t_IntersectExceptExpr = t_InstanceofExpr + ZeroOrMore(
    MatchFirst(Keyword("intersect"), Keyword("except")) + t_InstanceofExpr
)
t_IntersectExceptExpr.setName("IntersectExceptExpr")

t_UnionExpr = t_IntersectExceptExpr + ZeroOrMore(
    MatchFirst(Keyword("union") | Literal("|")) + t_IntersectExceptExpr
)
t_UnionExpr.setName("UnionExpr")
"""end Combining node sequences"""


""" Arithmetic Expressions """

tx_ArithmeticMultiplicativeSymbol = (
    Literal("*") | Keyword("div") | Keyword("idiv") | Keyword("mod")
)

t_ArithmeticAdditiveSymbol = Literal("+") | Literal("-")

tx_MultiplicativeExpr = t_UnionExpr + ZeroOrMore(
    tx_ArithmeticMultiplicativeSymbol + t_UnionExpr
)

tx_MultiplicativeExpr.setName("MultiplicativeExpr")

t_AdditiveExpr = tx_MultiplicativeExpr + ZeroOrMore(
    t_ArithmeticAdditiveSymbol + tx_MultiplicativeExpr
)
t_AdditiveExpr.setParseAction(get_additive_expr)
t_AdditiveExpr.setName("Additive_Expr")


t_RangeExpr = t_AdditiveExpr + Optional(Keyword("to") + t_AdditiveExpr)
t_RangeExpr.setName("RangeExpr")


def range_expr(toks):
    if len(toks) > 1:
        if toks[1] == "to":
            return range(toks[0], toks[2])

    # Don't return range if 'to' isn't found.
    return toks


t_RangeExpr.setParseAction(range_expr)

""" end Arithmetic Expressions"""


""" Comparison expressions """

t_ValueComp = (
    Keyword("eq")
    | Keyword("ne")
    | Keyword("lt")
    | Keyword("le")
    | Keyword("gt")
    | Keyword("ge")
)
t_ValueComp.setName("ValueComp")


t_GeneralComp = (
    Literal("=")
    | Literal("!=")
    | Literal("<")
    | Literal("<=")
    | Literal(">")
    | Literal(">=")
)
t_GeneralComp.setName("GeneralComp")


t_NodeComp = Keyword("is") | Keyword("<<") | Keyword(">>")
t_NodeComp.setName("NodeComp")

if xpath_version == "2.0":
    t_ComparisonExpr = t_RangeExpr + Optional(
        (t_ValueComp ^ t_GeneralComp ^ t_NodeComp) + t_RangeExpr
    )
    t_ComparisonExpr.setName("ComparisonExpr")
    t_ComparisonExpr.setParseAction(get_comparitive_expr)

elif xpath_version == "3.1":
    t_StringConcatExpr = t_RangeExpr + ZeroOrMore(Keyword("||") + t_AdditiveExpr)
    t_StringConcatExpr.setName("StringConcatExpr")

    t_ComparisonExpr = t_StringConcatExpr + Optional(
        (t_ValueComp | t_GeneralComp | t_NodeComp) + t_StringConcatExpr
    )
    t_ComparisonExpr.setName("ComparisonExpr")
    t_ComparisonExpr.setParseAction(get_comparitive_expr)


""" end Comparison expressions"""


class AndComparison:
    def __init__(self, values):
        self.values = values

    def answer(self):

        for value in self.values:
            if value is False:
                return False
        return True


class OrComparison:
    def __init__(self, values):
        self.values = values

    def answer(self):

        for value in self.values:
            if value is True:
                return True
        return False


def get_and(v):
    if len(v) > 1:
        if v[1] == "and":

            return AndComparison(values=[v[0], v[2]])

    return v


""" Logical Expressions """
t_AndExpr = t_ComparisonExpr + ZeroOrMore(Keyword("and") + t_ComparisonExpr)
t_AndExpr.setName("AndExpr")
t_AndExpr.setParseAction(get_and)


def get_or(v):
    if len(v) > 1:
        if v[1] in ["OR", "or"]:

            return OrComparison(values=[v[0], v[2]])

    return v


t_OrExpr = t_AndExpr + ZeroOrMore(Keyword("or") + t_AndExpr)
t_OrExpr.setName("OrExpr")
t_OrExpr.setParseAction(get_or)

""" end Logical Expressions """


""" Conditional Expression """
t_IfExpr = (
    Suppress(Keyword("if"))
    + l_par_l
    + t_Expr
    + l_par_r
    + Suppress(Keyword("then"))
    + t_ExprSingle
    + Suppress(Keyword("else"))
    + t_ExprSingle
)


t_IfExpr.setName("IfExpr")

""" end Conditional Expression """


t_IfExpr.setParseAction(
    lambda toks: IfExpression(test_expr=toks[0], then_expr=toks[1], else_expr=toks[2])
)


t_SimpleLetBinding = Literal("$") + t_VarName + Keyword(":=") + t_ExprSingle
t_SimpleLetBinding.setName("SimpleLetBinding")
t_SimpleLetClause = (
    Keyword("let") + t_SimpleLetBinding + ZeroOrMore(Literal(",") + t_SimpleLetBinding)
)
t_SimpleLetClause.setName("SimpleLetClause")

t_LetExpr = t_SimpleLetClause + Keyword("return") + t_ExprSingle
t_LetExpr.setName("LetExpr")

# Set ExprSingle with actual expressions

t_ExprSingle <<= t_IfExpr ^ t_ForExpr ^ t_OrExpr ^ t_QuantifiedExpr ^ t_LetExpr

t_XPath = t_Expr
t_XPath.setName("XPath")


# todo: Generating a railroad map requires Pyparsing 3.0. Uncomment when PP3.0 is released from beta
# def create_railroad():
#     from pyparsing.diagram import to_railroad, railroad_to_html
#
#     with open('/tmp/output.html', 'w') as fp:
#         railroad = to_railroad(t_Expr)
#         fp.write(railroad_to_html(railroad))
