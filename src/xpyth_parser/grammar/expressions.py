import functools
import operator
import types

import pyparsing
from pyparsing import (
    Combine,
    Literal,
    MatchFirst,
    Optional,
    OneOrMore,
    ZeroOrMore,
    Forward,
    Keyword,
    Suppress, Regex,
)

from .qualified_names import VariableRegistry
from ..conversion.functions.generic import QuerySingleton
from ..conversion.tests import processingInstructionTest, anyKindTest, textTest, commentTest, schemaAttributeTest, \
    elementTest, schemaElementTest, documentTest

var_reg = VariableRegistry()


from .literals import l_par_l, l_par_r, l_dot, t_NCName, t_IntegerLiteral, t_Literal, t_StringLiteral

from ..conversion.function import get_function, resolve_paths, cast_parameters
from ..conversion.qname import Parameter, qname_from_parse_results

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

# All these elements refer to QName
t_VarName = t_AtomicType = t_ElementName = t_TypeName = t_AttributeName = t_QName
t_VarName.setName("Varname")

def get_variable(toks):

    var_name = toks[0]

    if len(toks) > 1:
        return Parameter(qname=toks[0], type_declaration=toks[1])
    else:

        for var in var_reg.get_variable(toks[0]):
        # return Parameter(qname=v[0])
            if isinstance(var, str):

                parsed_var = t_XPath.parseString(var, parseAll=True)
                parsed_var = parsed_var[0].expr


                # try:
                #     # Parse the individual value as if it is an XPath expression
                #     parsed_var = t_XPath.parseString(var, parseAll=True)
                #
                #     # Unpack the outcome
                #     parsed_var = parsed_var[0].expr
                #
                # except:
                #     logging.warning(f"Could not parse parameter '{var_name}', value '{var}'")
                #     parsed_var = var

                yield parsed_var

            elif isinstance(var, int) or isinstance(var, float):
                yield var

            else:
                print("Really expected a string as variable")

t_VarRef = Suppress(Literal("$")) + t_VarName
t_VarRef.setParseAction(get_variable)
t_VarRef.setName("VarRef")

t_AtomicType.setName("AtomicType")
t_ElementName.setName("ElementName")
t_TypeName.setName("TypeName")
t_AttributeName.setName("AttributeName")



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

    def resolve_expression(self, test_outcome, variable_map, lxml_etree):

        # Then and Else are both SingleExpressions
        if test_outcome is True:
            # Test has succeeded, so we return the 'then' ExprSingle
            return_expr = resolve_expression(expression=self.then_expr, variable_map=variable_map, lxml_etree=lxml_etree)
        else:

            return_expr = resolve_expression(expression=self.else_expr, variable_map=variable_map, lxml_etree=lxml_etree)
        return return_expr


class PathExpression:
    def __init__(self, steps):

        if isinstance(steps, list):
            self.steps = steps
        else:
            self.steps = [steps]

    def to_str(self):
        return_string = ""
        for step in self.steps:
            return_string += str(step.axis) # ex: //
            return_string += str(step.step) # ex maindoc (qname)

            for predicate in step.predicatelist:
                return_string += f"[{str(predicate.val.expr)}]"
                # return_string += f"{str(predicate.val.expr)}"

        return return_string

    def resolve_path(self, lxml_etree):
        """
        Attempt to resolve path queries

        :param lxml_etree: LXML etree which the query is run against
        :return:
        """

        found_values = []
        if lxml_etree is not None:
            query_str = self.to_str()
            results = lxml_etree.xpath(query_str, namespaces=lxml_etree.nsmap)
            for result in results:
                # Try to cast the value to int if applicable.
                try:
                    found_values.append(int(result.text))
                except:
                    found_values.append(result.text)
        else:
            return None

        return found_values


def resolve_expression(expression, variable_map, lxml_etree, context_item_value=None):
    """
    Loops though parsed results using dynamic content. This is the main loop of our interpreting step


    :return:

    """

    # Set variable map and lxml etree. These should not be set at this time

    def resolve_fn(fn):
        """
        Wrapper function to run Functions
        :param fn:
        :return:
        """

        resolve_paths(fn=fn, lxml_etree=lxml_etree)
        # cast_parameters(fn=fn, paramlist=variable_map)

        # Then get the value by running the function
        value = fn()

        # Put the output value of the function into the AST as a number

        return value

    if isinstance(expression, XPath):
        # Expression needs to be unpacked:
        rootexpr = expression.expr
    else:
        rootexpr = expression

    if isinstance(rootexpr, int):
        # Is a primary
        return rootexpr

    elif isinstance(rootexpr, str):
        # Is a primary
        return rootexpr

    elif isinstance(rootexpr, float):
        # Is a primary
        return rootexpr

    elif isinstance(rootexpr, list):
        # Is a sequence with multiple values
        return rootexpr

    if isinstance(rootexpr, functools.partial):
        # Main node is a Function. Resolve this and add the answer to the Syntax Tree.
        # return rootexpr()
        function_outcome = rootexpr()
        if isinstance(function_outcome, types.GeneratorType):
            answers = []
            for ans in function_outcome:
                # todo: try to figure out if Functions should be yielding (generator) or returning.
                #  I'd say yield, because "fn:number(1 to 100)[. mod 5 eq 0]" should be a legal expression
                #  where 1 to 100 is cast as a number, and 'fed' through the predidicate filtering.
                answers.append(ans)
            return answers


        else:
            return function_outcome

        # return resolve_fn(rootexpr)

    elif isinstance(rootexpr, Parameter):
        param_value = rootexpr.resolve_parameter(paramlist=variable_map)
        return param_value

    elif isinstance(rootexpr, Operator):
        if context_item_value is None:
            rootexpr.resolve(variable_map, lxml_etree)


        return rootexpr.answer(variable_map=variable_map,
            lxml_etree=lxml_etree, context_item_value=context_item_value)

    elif isinstance(rootexpr, IfExpression):
        # Replace the if statement with its outcome

        # First get the outcome of the test by passing the test expression to the loop
        outcome_of_test = resolve_expression(
            expression=rootexpr.test_expr,
            variable_map=variable_map,
            lxml_etree=lxml_etree,
        )
        # Then, get the 'then' or 'else'  expression and continue
        return rootexpr.resolve_expression(test_outcome=outcome_of_test, variable_map=variable_map,
            lxml_etree=lxml_etree)

    elif isinstance(rootexpr, PostfixExpr):
        # Need to resolve the predicate (filter), pass  arguments to the rootexpr as if it is a function or perform a lookup
        return rootexpr.resolve_secondary(
            variable_map=variable_map,
            lxml_etree=lxml_etree,
        )

    elif isinstance(rootexpr, XPath):
        # Need to recursively run the child

        # Resolve the expression and substitute the expression for the answer
        return resolve_expression(
            expression=rootexpr,
            variable_map=variable_map,
            lxml_etree=lxml_etree,
        )

    elif isinstance(rootexpr, PathExpression):
        # Run the path expression against the LXML etree
        resolved_expr = rootexpr.resolve_path(lxml_etree=lxml_etree)
        # if resolved_expr is not None:
        return resolved_expr

    elif isinstance(rootexpr, Compare):
        # Pass data into the comparator

        if context_item_value is None:
            # If we are not dealing with a context item, we can 'collapse' the expression
            rootexpr.resolve(variable_map=variable_map, lxml_etree=lxml_etree, context_item_value=context_item_value)

        # Get answer
        return rootexpr.answer(variable_map=variable_map, lxml_etree=lxml_etree, context_item_value=context_item_value)
    elif isinstance(rootexpr, pyparsing.ParseResults):
        l = list(rootexpr)
        return l

    # Give back the now resolved expression
    return rootexpr

"""
TESTS
https://www.w3.org/TR/xpath20/#prod-xpath-KindTest
"""

t_ElementNameOrWildcard = t_ElementName | Literal("*")
t_ElementNameOrWildcard.setName("ElementNameOrWildcard")

t_ElementTest = (
    Keyword("element")
    + l_par_l
    + Optional(t_ElementNameOrWildcard + Optional("," + t_TypeName + Optional("?")))
    + l_par_r
)
t_ElementTest.setName("ElementTest")
t_ElementTest.setParseAction(elementTest)

t_ElementDeclaration = t_ElementName
t_ElementDeclaration.setName("ElementDeclaration")

t_SchemaElementTest = (
    Keyword("schema-element") + l_par_l + t_ElementDeclaration + l_par_r
)
t_SchemaElementTest.setParseAction(schemaElementTest)
t_SchemaElementTest.setName("schema-element")

t_DocumentTest = (
    Keyword("document-node")
    + l_par_l
    + Optional(t_ElementTest | t_SchemaElementTest)
    + l_par_r
)
t_DocumentTest.setName("DocumentTest")
t_DocumentTest.setParseAction(documentTest)

t_AttribNameOrWildcard = t_AttributeName | "*"
t_AttribNameOrWildcard.setName("AttribNameOrWildcard")

t_AttributeTest = (
    Keyword("attribute")
    + l_par_l
    + Optional(t_AttribNameOrWildcard + Optional("," + t_TypeName))
    + l_par_r
)
t_AttributeTest.setName("AttributeTest")

t_AttributeDeclaration = t_AttributeName
t_AttributeDeclaration.setName("AttributeDeclaration")

t_SchemaAttributeTest = (
    Keyword("schema-attribute") + l_par_l + t_AttributeDeclaration + l_par_r
)
t_SchemaAttributeTest.setParseAction(schemaAttributeTest)
t_SchemaAttributeTest.setName("SchemaAttributeTest")

t_CommentTest = Keyword("comment") + l_par_l + l_par_r
t_CommentTest.setParseAction(commentTest)
t_CommentTest.setName("comment")

t_TextTest = Keyword("text") + l_par_l + l_par_r
t_TextTest.setParseAction(textTest)
t_TextTest.setName("TextTest")

t_AnyKindTest = Keyword("node") + l_par_l + l_par_r
t_AnyKindTest.setParseAction(anyKindTest)
t_AnyKindTest.setName("AnyKindTest")

t_PITest = (
    Keyword("processing-instruction")
    + l_par_l
    + Optional(t_NCName | t_StringLiteral)
    + l_par_r
)
t_PITest.setParseAction(processingInstructionTest)
t_PITest.setName("Processing-InstructionTest")

t_KindTest = (
    t_ElementTest
    | t_AttributeTest
    | t_SchemaElementTest
    | t_SchemaAttributeTest
    | t_PITest
    | t_CommentTest
    | t_TextTest
    | t_AnyKindTest
    | t_DocumentTest
)
t_KindTest.setName("KindTest")
# Just as with t_NumericLiteral, the t_Wildcard order needed to be modified slightly
t_Wildcard = (
    (t_NCName + Literal(":") + Literal("*"))
    | (Literal("*") + Literal(":") + t_NCName)
    | Literal("*")
)
t_Wildcard.setName("Wildcard")

t_NameTest = t_QName | t_Wildcard
t_NameTest.setName("NameTest")

t_NodeTest = t_KindTest | t_NameTest
t_NodeTest.setName("NodeTest")


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

def parse_expr(toks):
    if len(toks) == 1:
        # Unpack the list
        return XPath(expr=toks[0])
    else:
        return XPath(expr=toks)


# t_Expr.setParseAction(lambda x: XPath(expr=x[0]))
t_Expr.setParseAction(parse_expr)



# https://www.w3.org/TR/xpath20/#doc-xpath-ContextItemExpr
class ContextItem:
    def __init__(self):
        self.value = None


t_ContextItemExpr = l_dot
t_ContextItemExpr.setName("ContextItemExpr")
t_ContextItemExpr.setParseAction(lambda: ContextItem())

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

t_BracedURILiteral = (
    Literal("Q") + Literal("{") + ZeroOrMore(Regex("[^{}]")) + Literal("}")
)
t_BracedURILiteral.setName("BracedURILiteral")

t_URIQualifiedName = t_BracedURILiteral + t_NCName
t_URIQualifiedName.setName("URIQualifiedName")

t_EQName = t_QName | t_URIQualifiedName
t_EQName.setName("EQName")

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

class PostfixExpr(Expr):
    def __init__(self, primary_expr, secondary=None):
        """
        A Postfix expression is a primary expression with either a predicate, argumentList or Lookup

        :param primary_expr:
        :param secondary:
        """

        self.expr = primary_expr

        if secondary is not None:
            if isinstance(secondary, list):
                self.secondary = secondary
            else:
                self.secondary = [secondary]

    def resolve_secondary(self, variable_map, lxml_etree):

        for secondary in self.secondary:
            if isinstance(secondary, Predicate):
                """
                Here I'd want to probably run the predicate (filter) for every instance of the primary expression.

                That would mean: make a generator of the primary expr.
                """

                filtered_items = []

                # Try each context_item
                for context_item in self.expr.expr:
                    ans = resolve_expression(
                        secondary.val,
                        variable_map=variable_map,
                        lxml_etree=lxml_etree,
                        context_item_value=context_item,
                    )

                    if ans is True:
                        filtered_items.append(context_item)

                # Return all items that match the predicate.
                return filtered_items
            else:
                # Lookup and arguments not yet supported
                pass

            pass  # Attempt to do something with the secondary expressions
        pass


def postfix_expr(toks):
    """
    A postfix expression is a primary expression with optionally either a predicate, argumentList or Lookup

    :param toks:
    :return:
    """

    if len(toks) > 1 and isinstance(toks[0], XPath):
        # We only need to create a PostfixExpr when there are secondary expressions to add.
        # Otherwise It'll just create overhead
        return PostfixExpr(toks[0], toks[1:])

    return toks


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
    t_PostfixExpr.setParseAction(postfix_expr)

    t_StepExpr = t_PostfixExpr | t_AxisStep
    t_StepExpr.setName("StepExpr")

class Axis:
    def __init__(self, axis, step, predicatelist=None):

        self.axis = axis
        self.step = step
        self.predicatelist = predicatelist if predicatelist is not None else []

    def __repr__(self):
        return f"axis: {self.axis}, step:{self.step}"


def get_single_path_expr(toks):

    if len(toks) == 2:
        return Axis(axis=toks[0], step=toks[1])
    elif len(toks) > 2:
        return Axis(axis=toks[0], step=toks[1], predicatelist=toks[2:])
    else:
        return toks


tx_SinglePathExpr = MatchFirst(Literal("//") | Literal("/")) + t_StepExpr
tx_SinglePathExpr.setParseAction(get_single_path_expr)

t_RelativePathExpr = t_StepExpr + ZeroOrMore(tx_SinglePathExpr)
t_RelativePathExpr.setName("RelativePathExpr")



def get_path_expr(toks):
    """

    :param toks:
    :return:
    """
    # todo: Can be ["//", QNAME, Predicate], but also [list of houndreds of paths from a variable]

    steps = []
    if toks[0] == "/" and len(toks) == 1:
        # https://www.w3.org/TR/xpath-3/#parse-note-leading-lone-slash
        return "/"

    elif toks[0] in ["/", "//"]:
        first_step = Axis(axis=toks[0], step=toks[1])

        if len(toks) > 2:
            for tok in toks[2:]:
                if isinstance(tok, Axis):
                    steps.append(tok)
                if isinstance(tok, Predicate):
                    first_step.predicatelist.append(tok)
            # If there are more then one step, add all of the steps to the list.
        #     steps = list(toks[2:])
        # else:
        #     steps = []

        steps.insert(0, first_step)

        """
        Dealing with abbreviated steps
        https://www.w3.org/TR/xpath-3/#abbrev
        """
    elif toks[0] == "@":
        # attribute::
        steps.append(Axis(axis="attribute::", step=toks[1]))
    elif toks[0] == "..":
        # parent::node()
        steps.append(Axis(axis="parent::node()", step=toks[1]))

    else:
        # If we didn't find anything axis-like, we probably need to return all toks
        return toks


    path_expression = PathExpression(steps=steps)
    # todo: Path expression also needs to be handled while parsing if we want partial functions to work.
    #  this probably means that we should let the whole 'parse first, intepret later' part go :/

    query_singleton = QuerySingleton()
    query = path_expression.to_str()
    if query_singleton.lxml_tree is not None:
        # Only try to query the lxml xpath if this actually exist
        result = query_singleton.lxml_tree.xpath(query, namespaces=query_singleton.lxml_tree.nsmap)
    else:
        return [None]

    if len(result) < 1:
        return [None]

    return result


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


def get_unary_expr(v):

    if len(v) > 1 and v[0] in ["+", "-"]:

        unary_op = UnaryOperator(operator=v[0], operand=v[1])
        return unary_op

    else:
        return v


t_UnaryExpr.setName("UnaryExpr")
t_UnaryExpr.setParseAction(get_unary_expr)



t_SingleType = t_AtomicType + Optional("?")
t_SingleType.setName("SingleType")

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


def get_nodes(l_values):
    # First loop though the whole equation and look for multiplication/dividing/modulo operators

    for i, val in enumerate(l_values):
        if val in ["*", "div", "mod"]:
            # if  val in [operator.mul, operator.truediv]:
            newlist = add_node(i=i, l_values=l_values)
            return get_nodes(newlist)

    # If mul/div operators have been handled, continue on with adding and subtracting
    for i, val in enumerate(l_values):
        # go though list of values, try to find operators in order of precedence.
        if val in ["+", "-"]:
            # if  val in [operator.add, operator.sub]:
            # Create a node for these
            newlist = add_node(i=i, l_values=l_values)
            return get_nodes(newlist)


def get_additive_expr(v):

    l_values = list(v)

    # Loop though the equation and create a nested tree of BinOp objects
    get_nodes(l_values)

    # If the final list only has one value, return that value instead of a list.

    if len(l_values) == 1:

        # We expect there to be only one value, which should be a BinOp.
        l_values = l_values[0]
        return l_values

    elif isinstance(l_values[0], BinaryOperator):
        # If the function gets called recursively, it could happen we already created the full expression.
        # In that case, just send it though.
        return l_values[0]

    else:
        # Is not a comparative expression
        return v


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


class SyntaxTreeNodeMixin(object):
    @property
    def _children(self) -> list:
        """
        Returns list with child nodes.

        """
        raise NotImplementedError

    def process_children(self):
        raise NotImplementedError


class Operator:
    pass

    @property
    def operator(self):
        # self.op does not show up in debugger. This is a workaround to see which operator is present.
        return str(self.op)

    def answer(self, variable_map, lxml_etree, context_item_value=None):
        """
        Returns the answer of the operator

        :param context_item_value:
        :return:
        """
        raise NotImplementedError

    def resolve(self, variable_map, lxml_etree):
        """
        Resolves the operator by calling the resolve_expression loop on its children

        :param variable_map:
        :param lxml_etree:
        :return:
        """

        raise NotImplementedError


class UnaryOperator(SyntaxTreeNodeMixin, Operator):
    def __init__(self, operand, operator):
        self.operand = operand
        self.op = operator

    def resolve(self, variable_map, lxml_etree):
        """
        Resolve parameter, path expression and context item of children

        :param variable_map:
        :param lxml_etree:
        :return:
        """

        if isinstance(self.operand, functools.partial):

            resolve_paths(fn=self.operand, lxml_etree=lxml_etree)
            # cast_parameters(fn=self.operand, paramlist=variable_map)
        else:
            print("Operand of unary operator type not known")

    def answer(self, variable_map, lxml_etree, context_item_value=None):

        if isinstance(self.operand, int):
            # If the value is an int, we can just use this value
            operand = self.operand

        elif isinstance(self.operand, Operator):
            # If the value is an Operator, we need to get to calculate its value first
            operand = self.operand.answer()

        elif isinstance(self.operand, functools.partial):
            # Get the value from the function
            operand = self.operand()

        else:

            # Is an XPath expression that needs to be resolved.
            operand = self.operand.resolve_expression()

        if self.op == "+":
            return +operand
        elif self.op == "-":
            return -operand
        else:
            raise ("Unknown unary operator")

    @property
    def _children(self):
        return [self.operand]

    def process_children(self):
        new_operand = yield self.operand
        if new_operand is not None:
            self.operand = new_operand


class BinaryOperator(SyntaxTreeNodeMixin, Operator):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    @property
    def _children(self) -> list:
        return [self.left, self.right]

    def process_children(self):
        new_left = yield self.left
        if new_left is not None:
            self.left = new_left

        new_right = yield self.right
        if new_right is not None:
            self.right = new_right

    def resolve(self, variable_map, lxml_etree):
        """
        Resolve parameter, path expression and context item of children

        :param variable_map:
        :param lxml_etree:
        :return:
        """
        if isinstance(self.left, functools.partial):

            resolve_paths(self.left, lxml_etree=lxml_etree)
            # self.left.resolve_paths(lxml_etree=lxml_etree)
            # cast_parameters(self.left, paramlist=variable_map)
            # self.left.cast_parameters(paramlist=variable_map)


        if isinstance(self.right, functools.partial):
            # self.right.resolve_paths(lxml_etree=lxml_etree)
            # self.right.cast_parameters(paramlist=variable_map)

            resolve_paths(self.right, lxml_etree=lxml_etree)
            # cast_parameters(self.right, paramlist=variable_map)

    def answer(self, variable_map, lxml_etree, context_item_value=None):

        if isinstance(self.left, int) or isinstance(self.left, float):
            # If the value is an int, we can just use this value
            left = self.left

        elif isinstance(self.left, Operator):
            # If the value is an Operator, we need to get to calculate its value first
            left = resolve_expression(expression=self.left, variable_map=variable_map, lxml_etree=lxml_etree)

            # left = left.answer()

        elif isinstance(self.left, functools.partial):
            # Get the value from the function

            left = self.left()

        elif isinstance(self.left, ContextItem):
            left = context_item_value

        else:

            # Is an XPath expression that needs to be resolved.
            left = self.left.resolve_child()

        if isinstance(self.right, int) or isinstance(self.right, float):
            right = self.right

        elif isinstance(self.right, Operator):
            right = resolve_expression(expression=self.right, variable_map=variable_map, lxml_etree=lxml_etree)

            # If the value is an Operator, we need to get to calculate its value first
            # right = right.answer()

        elif isinstance(self.right, functools.partial):
            # Get the value from the function
            right = self.right()

        elif isinstance(self.right, ContextItem):
            right = context_item_value

        else:
            # Is an XPath expression that needs to be resolved.
            right = self.right.resolve_child()

        return self.op(left, right)


arth_ops = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "div": operator.truediv,
    "mod": operator.mod,
}


def add_node(i, l_values):

    # Take operator and expressions out of the list

    expr_right = l_values.pop(i + 1)

    op = l_values.pop(i)
    op = arth_ops[op]

    expr_left = l_values.pop(i - 1)

    # get the node
    node = BinaryOperator(expr_left, op, expr_right)

    l_values.insert(i - 1, node)

    return l_values


class Compare(SyntaxTreeNodeMixin):
    def __init__(self, left, op, comparators):
        self.left = left
        #
        # if len(op) != len(comparators):
        #     raise ValueError(
        #         f"Got {len(op)} operators and {len(comparators)} comparators to compare"
        #     )
        self.op = op

        if not isinstance(comparators, list):
            comparators = [comparators]
        self.comparators = comparators

    @property
    def _children(self) -> list:
        return [self.left] + self.comparators

    def process_children(self):
        new_left = yield self.left
        if new_left is not None:
            self.left = new_left

        for i, comparator in enumerate(self.comparators):
            new_comparator = yield comparator
            if new_comparator is not None:
                self.comparators[i] = new_comparator

    def resolve(self, variable_map, lxml_etree, context_item_value):

        for i, child in enumerate(self.comparators):
            ans = resolve_expression(
                child,
                variable_map=variable_map,
                lxml_etree=lxml_etree,
                context_item_value=context_item_value
            )
            if ans is not None:
                self.comparators[i] = ans

        # Do the same with the left operand
        ans_left = resolve_expression(
            self.left,
            variable_map=variable_map,
            lxml_etree=lxml_etree,
            context_item_value=context_item_value
        )
        if ans_left is not None:
            self.left = ans_left

    def answer(self, variable_map, lxml_etree, context_item_value=None):
        """
        Gives the answer of the Operator. If the operator contains any nested functions,
        they will be resolved automatically.

        so if isinstance(self.left, Function), this child will first be ran.

        :return: Answer of operator
        """
        if isinstance(self.left, functools.partial):
            left = self.left()

        elif isinstance(self.left, Operator):
            # Need to get the value of the operator
            left = self.left.answer(variable_map=variable_map, lxml_etree=lxml_etree, context_item_value=context_item_value)

        elif isinstance(self.left, ContextItem):
            left = context_item_value

        else:
            left = self.left

        for i, comparator in enumerate(self.comparators):

            # Resolve function or operator if this is a nested function
            if isinstance(comparator, functools.partial):
                self.comparators[i] = comparator()
                comparator = comparator()

            elif isinstance(comparator, Operator):
                self.comparators[i] = comparator.answer()
                comparator = comparator.answer()

            elif isinstance(self.comparators[i], ContextItem):
                comparator = context_item_value

            if self.op(left, comparator) is False:
                return False

        return True


class CompareValue(Compare):
    # https://www.w3.org/TR/xpath-3/#id-value-comparisons
    pass


class CompareGeneral(Compare):
    # https://www.w3.org/TR/xpath-3/#id-general-comparisons
    pass


class CompareNode(Compare):
    # https://www.w3.org/TR/xpath-3/#id-node-comparisons
    pass


comp_expr = {
    "=": operator.is_,  # General comparison
    "eq": operator.eq,  # value comparison
    "!=": operator.is_not,
    "ne": operator.ne,
    "<": "<",
    "lt": operator.lt,
    "<=": "<=",
    "le": operator.le,
    ">": ">",
    "gt": operator.gt,
    ">=": ">=",
    "ge": operator.ge,
}


def get_comparitive_expr(toks):
    if len(toks) > 2:
        left = toks[0]
        operator = toks[1]
        comparators = toks[2]

        # if isinstance(comparators, int) or isinstance(comparators, str):
        #     # Wrap one element into list
        #     comparators = [comparators]

        # Only add a comparative expression if a comparator symbol has been found
        if operator in comp_expr.keys():
            py_op = comp_expr[operator]

            # todo: should probably leave this to the parser. But maybe there is something we'd like the check
            if operator in ["eq", "ne", "lt", "le", "gt", "ge"]:
                return CompareValue(left=left, op=py_op, comparators=comparators)
            elif operator in ["=", "!=", "<", "<=", ">", ">="]:
                return CompareGeneral(left=left, op=py_op, comparators=comparators)
            elif operator in ["is", "<<", ">>"]:
                return CompareNode(left=left, op=py_op, comparators=comparators)

    return toks


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
