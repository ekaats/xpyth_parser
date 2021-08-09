import ast

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
)
from ..conversion.expressions import IfExpression
from ..conversion.function import get_function
from ..conversion.functions.generic import Function, Datatype
from ..conversion.path import get_single_path_expr, get_path_expr, PathExpression
from ..conversion.qname import Parameter

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


def resolve_simple_expression(expression, variable_map, lxml_etree):
    """
    Resolve simple expressions (ExprSingle in grammar)

    :param expression:
    :param variable_map:
    :param lxml_etree:
    :return:
    """

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
        return ast.Constant(value)

    # All non AST nodes should be resolved before this point, so here we can assume an AST node to be the root.
    for node in ast.walk(expression):
        if hasattr(node, "comparators"):

            """Go through comparators and replace these with AST nodes based on the variable map"""
            for i, comparator in enumerate(node.comparators):
                if isinstance(comparator, Parameter):
                    # Recast the parameter based on information from the variable_map
                    comparator = comparator.get_ast_node(variable_map)
                    node.comparators[i] = comparator
                elif isinstance(comparator, XPath):
                    # Need to recursively run the child
                    # Pass information to child

                    resolved_child_expr = resolve_expression(
                        expression=comparator,
                        variable_map=variable_map,
                        lxml_etree=lxml_etree,
                    )
                    node.comparators[i] = resolved_child_expr

        if hasattr(node, "values"):

            for i, value in enumerate(node.values):
                if isinstance(value, Parameter):
                    # Recast the parameter based on information from the variable_map
                    value = value.get_ast_node(variable_map)
                    node.values[i] = value

                elif isinstance(value, Function):
                    node.values[i] = resolve_fn(value)

        if hasattr(node, "operand"):

            # First cast parameters based on variable map
            if isinstance(node.operand, Function):
                # Run the function and add the outcome as a value to the operand
                node.operand = resolve_fn(node.operand)

        if hasattr(node, "left"):
            if isinstance(node.left, Function):
                node.left = resolve_fn(node.left)
            elif isinstance(node.left, XPath):
                node.left = resolve_expression(
                    expression=node.left,
                    variable_map=variable_map,
                    lxml_etree=lxml_etree,
                )

        if hasattr(node, "right"):
            if isinstance(node.right, Function):
                node.right = resolve_fn(node.right)
            elif isinstance(node.right, XPath):
                node.right = resolve_expression(
                    expression=node.right,
                    variable_map=variable_map,
                    lxml_etree=lxml_etree,
                )
    return expression


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

        return ast.Constant(value)

    # for i, parsed_expr in enumerate(expression.expr):

    if isinstance(expression.expr, Function):
        # Main node is a Function. Resolve this and add the answer to the AST.
        expression.expr = resolve_fn(expression.expr)

    elif isinstance(expression.expr, Datatype):
        # Syntactically simmilar to a Function, but a datatype should not be wrapped
        pass

    elif isinstance(expression.expr, IfExpression):
        # every Expr should be resolvable by itexpression.
        test_expr = resolve_expression(
            expression=expression.expr.test_expr,
            variable_map=variable_map,
            lxml_etree=lxml_etree,
        )

        fixed = ast.fix_missing_locations(ast.Expression(test_expr))
        try:
            compiled_expr = compile(fixed, "", "eval")
        except:
            raise Exception
        else:
            evaluated_expr = eval(compiled_expr)

        outcome = expression.expr.resolve_expression(
            test_outcome=evaluated_expr,
            variable_map=variable_map,
            lxml_etree=lxml_etree,
        )

        # Replace the if statement with its outcome
        expression.expr = outcome

    elif isinstance(expression.expr, XPath):
        # Need to recursively run the child

        # Resolve the expression and substitute the expression for the answer
        resolved_expr = resolve_expression(
            expression=expression.expr, variable_map=variable_map, lxml_etree=lxml_etree
        )
        expression.expr = resolved_expr

    elif isinstance(expression.expr, PathExpression):
        # Run the path expression against the LXML etree
        resolved_expr = expression.expr.resolve_path(lxml_etree=lxml_etree)
        # if resolved_expr is not None:
        expression.expr = resolved_expr

    else:
        expression.expr = resolve_simple_expression(
            expression=expression.expr, variable_map=variable_map, lxml_etree=lxml_etree
        )

    # Give back the now resolved expression
    return expression.expr


class XPath:
    def __init__(self, expr, variable_map=None, xml_etree=None):

        self.expr = expr

        self.variable_map = variable_map if variable_map else {}
        self.lxml_etree = xml_etree

    def get_expression(self):
        """
        Returns XPath expression wrapped into an ast.Expression.
        An XPath expression should resolve into one part,
        but sometimes this is not the case. expr_nr be used to select a different part of the expression.

        :arg: expr_nr: int
        :return: ast.Expression
        """
        return ast.Expression(self.expr)


def wrap_expr(v):
    expression = v[0]

    return XPath(expr=expression)


t_Expr = t_ExprSingle + ZeroOrMore(Literal(","), t_ExprSingle)
t_Expr.setName("Expr")
t_Expr.setParseAction(wrap_expr)
# https://www.w3.org/TR/xpath20/#doc-xpath-ParenthesizedExpr


# https://www.w3.org/TR/xpath20/#doc-xpath-ContextItemExpr
t_ContextItemExpr = l_dot
t_ContextItemExpr.setName("ContextItemExpr")

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
    print(f"Getting predicate: {v[0]}")
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
t_UnaryExpr = ZeroOrMore(Literal(" -") | Literal("+")) + t_ValueExpr

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

# Todo: Cast GeneralComp in to pythonic operators. Could we use the same as for ValueComp?
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


def get_and(v):
    if len(v) > 1:
        if v[1] == "and":
            a = v[0]
            b = v[2]

            and_op = ast.BoolOp(op=ast.And(), values=[a, b])
            return ast.fix_missing_locations(and_op)
    return v


""" Logical Expressions """
t_AndExpr = t_ComparisonExpr + ZeroOrMore(Keyword("and") + t_ComparisonExpr)
t_AndExpr.setName("AndExpr")
t_AndExpr.setParseAction(get_and)


def get_or(v):
    if len(v) > 1:
        if v[1] in ["OR", "or"]:
            a = v[0]

            if isinstance(v[2], int):
                b = ast.Constant(v[2])
            else:
                b = v[2]

            or_op = ast.BoolOp(op=ast.Or(), values=[a, b])
            return ast.fix_missing_locations(or_op)
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
