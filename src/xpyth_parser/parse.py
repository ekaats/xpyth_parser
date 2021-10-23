from lxml import etree
from lxml.etree import Element
from typing import Union, Optional
from .grammar.expressions import t_XPath, resolve_expression
from .conversion.functions.generic import FunctionRegistry, QuerySingleton
from .grammar.qualified_names import VariableRegistry



class Parser:
    def __init__(
        self,
        xpath_expr: str,
        parseAll: bool = True,
        variable_map: Optional[dict] = None,
        xml:Union[bytes, str, Element, None] = None,
        context_item: Union[str, list, None] = None,
        no_resolve=False,
        custom_functions=None
    ):
        """

        :param xpath_expr: String of the XPath expression
        :param parseAll: Boolean passed to PyParsing. If set to true, Parsing will fail if any part of the string is not understood.
        :param variable_map: Dict of variables which Parameters can be mapped to.
        :param xml: Byte string of an XML object to be parsed
        :param no_resolve: If set to True, only grammar is parsed but the expression is not resolved. This can be used for debugging.

        For example:
        parsed_expr = Parser("(1 + 2) = (2 + 1)")
        parsed_expr.XPath would contain the resolved tree
        parsed_expr.resolved_answer == True. This is the answer of the expression
        """

        # First, add the custom functions to the function registry.
        FunctionRegistry(custom_functions=custom_functions)
        VariableRegistry(variables=variable_map)

        if xml is not None:
            if isinstance(xml, bytes):
                tree = etree.fromstring(xml)
            elif isinstance(xml, str):
                tree = etree.fromstring(bytes(xml, encoding="utf-8"))

            else:
                tree = xml

            QuerySingleton(lxml_tree=tree)

            self.lxml_etree = tree
        else:
            self.lxml_etree = None

        self.no_resolve = no_resolve

        if isinstance(xpath_expr, str):
            # Parse the Grammar

            parsed_grammar = t_XPath.parseString(xpath_expr, parseAll=parseAll)
            if len(parsed_grammar) > 1:
                raise ("Did not expect more than 1 expressions")
            else:
                self.XPath = parsed_grammar[0]
                self.XPath.xml_etree = self.lxml_etree
        else:
            print("Expected a string as input for an XPath Expression")

        # Add variable map to self and child expression
        self.XPath.variable_map = variable_map if variable_map else {}
        self.variable_map = variable_map if variable_map else {}

        self.context_item = context_item

        # Set resolved_answer to None:
        self.resolved_answer = None

        if no_resolve is False:
            # Resolve parameters and path queries the of expression
            self.resolved_answer = resolve_expression(
                expression=self.XPath,
                variable_map=self.variable_map,
                lxml_etree=self.lxml_etree,
            )


    def run(self):
        """
        Run the expression.

        :return: Result of XPath expression
        """
        if self.no_resolve is True:

            answer = resolve_expression(
                expression=self.XPath,
                variable_map=self.variable_map,
                lxml_etree=self.lxml_etree,
            )
        else:
            # Otherwise return the answer that is resolved beforehand
            return self.resolved_answer

        return answer
