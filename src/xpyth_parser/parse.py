import ast
from lxml import etree

from .grammar.expressions import t_XPath, resolve_expression


class ResolveQnames(ast.NodeTransformer):
    def visit_QName(self, node):
        print("")




class Parser:
    def __init__(self, xpath_expr, parseAll=True, variable_map=None, xml=None, no_resolve=False):
        """

        :param xpath_expr: String of the XPath expression
        :param parseAll:
        :param variable_map: List of variables which Parameters can be mapped to.
        :param xml: Byte string of an XML object to be parsed
        :param no_resolve: If set to True, only grammar is parsed but the expression is not resolved
        """
        if isinstance(xpath_expr, str):
            # Parse the Grammar

            parsed_grammar = t_XPath.parseString(xpath_expr, parseAll=parseAll)
            if len(parsed_grammar) > 1:
                raise("Did not expect more than 1 expressions")
            else:
                self.XPath = parsed_grammar[0]
        else:
            print("Expected a string as input for an XPath Expression")

        # Add variable map to self and child expression
        self.XPath.variable_map = variable_map if variable_map else {}
        self.variable_map = variable_map if variable_map else {}


        if xml:
            tree = etree.fromstring(xml)
            self.XPath.xml_etree = tree
            self.lxml_etree = tree
        else:
            self.lxml_etree = None


        self.no_resolve = no_resolve
        if no_resolve is False:
            # Resolve parameters and path queries the of expression
            resolve_expression(expression=self.XPath, variable_map=self.variable_map, lxml_etree=self.lxml_etree)

    def run(self):
        """
        :return: Result of XPath expression
        """
        if self.no_resolve is True:
            # If no_resolve was set to true, resolve now before running the AST.
            self.XPath.resolve_expression()

        fixed = ast.fix_missing_locations(self.XPath.get_expression())
        try:
            compiled_expr = compile(fixed, "", "eval")
        except:
            raise Exception
        else:
            evaluated_expr = eval(compiled_expr)
            return evaluated_expr

