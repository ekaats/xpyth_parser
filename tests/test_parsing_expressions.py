import unittest
import operator
from ast import BinOp, Compare
from src.xpyth_parser.conversion.functions.generic import Function
from src.xpyth_parser.conversion.qname import QName
from src.xpyth_parser.grammar.expressions import t_PrimaryExpr, t_UnaryExpr, t_AdditiveExpr, t_XPath, t_ParenthesizedExpr


class ExpressionTests(unittest.TestCase):



    def test_expressions(self):
        """
        Run tests which validate simple expressions

        :return:
        """
        # Var ref
        self.assertEqual(list(t_XPath.parseString("var:ref", parseAll=True)), [QName(prefix="var", localname='ref')])

        # Parenthesized Expression

        self.assertTrue(Compare(list(t_AdditiveExpr.parseString("1 + 2", parseAll=True)), BinOp(1, operator.add, 2)))

        self.assertTrue(Compare(list(t_ParenthesizedExpr.parseString("(1 + 2)", parseAll=True)),
                         [BinOp(1, operator.add, 2)]))

        self.assertTrue(Compare(list(t_XPath.parseString("(1 + 2 * 3) * (3 - 5)", parseAll=True)),
                         [BinOp(1, operator.add, BinOp(2, operator.mul, 3)), operator.mul, BinOp(3, operator.sub, 5),]))


        self.assertTrue(Compare(list(t_XPath.parseString("(1 + 2 * 3 - 4 / 5 * 6 - 7) * (3 - 5)", parseAll=True)),
                         [
                             BinOp(
                                 BinOp(
                                     BinOp(
                                         BinOp(
                                             BinOp(
                                                 BinOp(
                                                     BinOp(
                                                         BinOp(
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
                             BinOp(
                                 3, operator.sub, 5
                             )
                         ]))

        self.assertTrue(Compare(list(t_XPath.parseString("(1 + 2 + localname) * (3 - 5)", parseAll=True)),
                         [
                             BinOp(BinOp(1, operator.add, 2), operator.add, QName(localname="localname")),
                             operator.mul, BinOp(3, operator.sub, 5)]))


        # Context Item Expression
        self.assertEqual(list(t_PrimaryExpr.parseString(".", parseAll=True)), ["."])

        # Function Call
        self.assertEqual(list(t_PrimaryExpr.parseString("my:function(1,2)", parseAll=True)),
                         [Function(qname=QName(prefix="my", localname="function"), arguments=(1, 2))])


    def test_operators(self):
        """
        Test operative expressions
        """
        self.assertEqual(list(t_UnaryExpr.parseString(f"+ 1", parseAll=True)), ["+", 1])
        # self.assertEqual(list(t_UnaryExpr.parseString(f" - localname", parseAll=True)), ["-", QName(localname="localname")])
        self.assertEqual(list(t_UnaryExpr.parseString("+ ()", parseAll=True)), ["+", ()])

        # Additive Expressions
        self.assertTrue(Compare(list(t_AdditiveExpr.parseString("1 + 1", parseAll=True)), [1, operator.add, 1]))

