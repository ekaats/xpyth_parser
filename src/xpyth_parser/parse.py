import ast

from .grammar.expressions import t_XPath


class XPath:

    def __init__(self, xpath_expr, parseAll=True):
        self.XPath = t_XPath.parseString(xpath_expr, parseAll=parseAll)

    def get_expression(self, expr_nr=0):
        """
        Returns XPath expression wrapped into an ast.Expression.
        An XPath expression should resolve into one part,
        but sometimes this is not the case. expr_nr be used to select a different part of the expression.

        :arg: expr_nr: int
        :return: ast.Expression
        """
        return ast.Expression(self.XPath[expr_nr])

    def eval_expression(self):
        """
        :return: Result of XPath expression
        """
        fixed = ast.fix_missing_locations(self.get_expression())
        compiled_expr = compile(fixed, "", "eval")
        evaluated_expr = eval(compiled_expr)
        return evaluated_expr