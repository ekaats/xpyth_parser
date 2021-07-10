import unittest
import operator
import ast
import pyparsing
from src.xpyth_parser.conversion.functions.generic import Function
from src.xpyth_parser.conversion.qname import QName
from src.xpyth_parser.grammar.expressions import t_PrimaryExpr, t_UnaryExpr, t_AdditiveExpr, t_XPath, t_ParenthesizedExpr
from src.xpyth_parser.parse import XPath


class ExpressionTests(unittest.TestCase):



    def test_expressions(self):
        """
        Run tests which validate simple expressions

        :return:
        """
        # Var ref
        self.assertEqual(list(t_XPath.parseString("var:ref", parseAll=True)), [QName(prefix="var", localname='ref')])

        # Parenthesized Expression

        self.assertTrue(ast.Compare(list(t_AdditiveExpr.parseString("1 + 2", parseAll=True)), ast.BinOp(1, operator.add, 2)))

        self.assertTrue(ast.Compare(list(t_ParenthesizedExpr.parseString("(1 + 2)", parseAll=True)),
                         [ast.BinOp(1, operator.add, 2)]))

        self.assertTrue(ast.Compare(list(t_XPath.parseString("(1 + 2 * 3) * (3 - 5)", parseAll=True)),
                         [ast.BinOp(1, operator.add, ast.BinOp(2, operator.mul, 3)), operator.mul, ast.BinOp(3, operator.sub, 5),]))


        self.assertTrue(ast.Compare(list(t_XPath.parseString("(1 + 2 * 3 - 4 div 5 * 6 - 7) * (3 - 5)", parseAll=True)),
                         [
                             ast.BinOp(
                                 ast.BinOp(
                                     ast.BinOp(
                                         ast.BinOp(
                                             ast.BinOp(
                                                 ast.BinOp(
                                                     ast.BinOp(
                                                         ast.BinOp(
                                                             1, operator.add, 2
                                                         ),
                                                         operator.mul, 3
                                                     ),

                                                 ),
                                                 operator.sub,  4
                                             ),
                                             operator.truediv, 5
                                               ),
                                         operator.mul, 6
                                     )
                                 ),
                                 operator.sub,  7
                             ),
                             operator.mul,
                             ast.BinOp(
                                 3, operator.sub, 5
                             )
                         ]))

        self.assertTrue(ast.Compare(list(t_XPath.parseString("(1 + 2 + localname) * (3 - 5)", parseAll=True)),
                         [
                             ast.BinOp(ast.BinOp(1, operator.add, 2), operator.add, QName(localname="localname")),
                             operator.mul, ast.BinOp(3, operator.sub, 5)]))


        # Context Item Expression
        self.assertEqual(list(t_PrimaryExpr.parseString(".", parseAll=True)), ["."])

        # Function Call
        self.assertEqual(list(t_PrimaryExpr.parseString("my:function(1,2)", parseAll=True)),
                         [Function(qname=QName(prefix="my", localname="function"), arguments=(1, 2))])


    def test_operators(self):
        """
        Test operative expressions
        """
        self.assertTrue(ast.Compare(list(t_UnaryExpr.parseString(f"+ 1", parseAll=True)), [ast.UnaryOp("+", 1)]))
        self.assertTrue(ast.Compare(list(t_XPath.parseString(f"+ 1", parseAll=True)), [ast.UnaryOp("+", 1)]))
        # self.assertEqual(list(t_UnaryExpr.parseString(f" - localname", parseAll=True)), ["-", QName(localname="localname")])
        self.assertTrue(ast.Compare(list(t_UnaryExpr.parseString("+ (1 + 2)", parseAll=True)), [ast.UnaryOp("+", ast.BinOp(1, "+", 2))]))



        # The unary expression before a function should parse correctly
        self.assertTrue(ast.Compare(list(XPath("+ sum(1,3)", parseAll=True).XPath), [ast.UnaryOp("+", Function(qname=QName(localname=sum), arguments=(1,3)))]))

        # Additive Expressions
        self.assertTrue(ast.Compare(list(t_AdditiveExpr.parseString("1 + 1", parseAll=True)), [1, operator.add, 1]))

    def test_compile_arithmetic(self):

        def wrapper(calc_str):
            """
            Haven't found a way to wrap the top expression into an ast.Expression.
            This is an issue with parenthesized strings
            """
            xpath_query = list(t_XPath.parseString(calc_str, parseAll=True))[0]
            xpath_expr = ast.Expression(xpath_query)
            fixed = ast.fix_missing_locations(xpath_expr)
            evaluation = eval(compile(fixed, "", "eval"))


            return evaluation

        self.assertEqual(wrapper("1 + 2"), 3)
        self.assertEqual(wrapper("(3 - 5)"), -2)
        self.assertEqual(wrapper("(4 + 3 - 5)"), 2)
        self.assertEqual(wrapper("(4 + 3 * 5)"), 19)
        self.assertEqual(wrapper("(4 + 3 * 5) - 9"), 10)
        self.assertEqual(wrapper("(1 + 2 * 3 - 4 div 5 * 6 - 7) * (3 - 5)"), 9.600000000000001)