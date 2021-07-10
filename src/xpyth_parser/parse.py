import ast

from .grammar.expressions import t_XPath


class XPath:

    def __init__(self, xpath_expr, parseAll=True):
        self.XPath = t_XPath.parseString(xpath_expr, parseAll=parseAll)

    def get_expression(self):
        """
        Returns XPath expression wrapped into an ast.Expression

        :return: ast.Expression
        """
        return ast.Expression(self.XPath)

    def eval_expression(self):
        """

        :return: Result of XPath expression
        """
        fixed = ast.fix_missing_locations(self.get_expression())
        return eval(compile(fixed, "", "eval"))