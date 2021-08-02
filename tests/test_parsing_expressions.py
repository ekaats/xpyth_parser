import unittest
import operator
import ast
import pyparsing
from src.xpyth_parser.conversion.functions.generic import Function
from src.xpyth_parser.conversion.qname import QName
from src.xpyth_parser.grammar.expressions import (
    t_PrimaryExpr,
    t_UnaryExpr,
    t_AdditiveExpr,
    t_XPath,
    t_ParenthesizedExpr,
)
from src.xpyth_parser.parse import XPath


class ExpressionTests(unittest.TestCase):
    def test_expressions(self):
        """
        Run tests which validate simple expressions

        :return:
        """
        # Var ref
        self.assertEqual(
            list(t_XPath.parseString("var:ref", parseAll=True)),
            [QName(prefix="var", localname="ref")],
        )

        # Parenthesized Expression
        l1 = list(t_AdditiveExpr.parseString("1 + 2", parseAll=True))
        self.assertEqual(l1[0].left.value, 1)
        self.assertTrue(isinstance(l1[0].op, ast.Add))
        self.assertEqual(l1[0].right.value, 2)

        l2 = list(t_ParenthesizedExpr.parseString("(1 + 2)", parseAll=True))
        self.assertEqual(l2[0].left.value, 1)
        self.assertTrue(isinstance(l2[0].op, ast.Add))
        self.assertEqual(l2[0].right.value, 2)

        l3 = list(t_XPath.parseString("(1 + 2 * 3) * (3 - 5)", parseAll=True))
        self.assertEqual(l3[0].left.left.value, 1)
        self.assertTrue(isinstance(l3[0].left.op, ast.Add))

        self.assertEqual(l3[0].left.right.left.value, 2)
        self.assertTrue(isinstance(l3[0].left.right.op, ast.Mult))
        self.assertEqual(l3[0].left.right.right.value, 3)

        self.assertTrue(isinstance(l3[0].op, ast.Mult))
        self.assertEqual(l3[0].right.left.value, 3)
        self.assertTrue(isinstance(l3[0].right.op, ast.Sub))
        self.assertEqual(l3[0].right.right.value, 5)

        l4 = list(t_XPath.parseString("(2 + localname)", parseAll=True))
        self.assertEqual(l4[0].left.value, 2)
        self.assertTrue(isinstance(l4[0].op, ast.Add))
        self.assertEqual(l4[0].right, QName(localname="localname"))

        # Context Item Expression
        self.assertEqual(list(t_PrimaryExpr.parseString(".", parseAll=True)), ["."])

        # Function Call
        l6 = list(t_PrimaryExpr.parseString("my:function(1,2)", parseAll=True))
        self.assertTrue(isinstance(l6[0], Function))
        self.assertEqual(l6[0].qname, QName(prefix="my", localname="function"))
        self.assertEqual(l6[0].arguments[0].value, 1)
        self.assertEqual(l6[0].arguments[1].value, 2)

                #
        #     [

        #             qname=, arguments=(1, 2)
        #         )
        #     ],
        # )

    def test_operators(self):
        """
        Test operative expressions
        """
        l1 = list(t_UnaryExpr.parseString(f"+ 1", parseAll=True))
        self.assertTrue(isinstance(l1[0], ast.UnaryOp))
        self.assertTrue(isinstance(l1[0].op, ast.UAdd))
        self.assertEqual(l1[0].operand.value, 1)

        l2 = list(t_XPath.parseString(f"+ 1", parseAll=True))
        self.assertTrue(isinstance(l2[0], ast.UnaryOp))
        self.assertTrue(isinstance(l2[0].op, ast.UAdd))
        self.assertEqual(l2[0].operand.value, 1)

        l3 = list(t_UnaryExpr.parseString("+ (1 + 2)", parseAll=True))
        self.assertTrue(isinstance(l3[0], ast.UnaryOp))
        self.assertTrue(isinstance(l3[0].op, ast.UAdd))

        self.assertTrue(isinstance(l3[0].operand, ast.BinOp))
        self.assertEqual(l3[0].operand.left.value, 1)
        self.assertTrue(isinstance(l3[0].operand.op, ast.Add))
        self.assertEqual(l3[0].operand.right.value, 2)

        l4 = list(XPath("+ sum(1,3)", parseAll=True).XPath)
        self.assertTrue(isinstance(l4[0], ast.UnaryOp))
        self.assertTrue(isinstance(l4[0].op, ast.UAdd))
        # The unary expression before a function should parse correctly

        self.assertTrue(isinstance(l4[0].operand, Function))
        self.assertEqual(l4[0].operand.qname, QName(prefix="fn", localname="sum"))
        self.assertEqual(l4[0].operand.arguments[0].value, 1)
        self.assertEqual(l4[0].operand.arguments[1].value, 3)

    def test_compile_arithmetic(self):

        self.assertEqual(XPath("1 + 2").eval_expression(), 3)
        self.assertEqual(XPath("(3 - 5)").eval_expression(), -2)
        self.assertEqual(XPath("(4 + 3 - 5)").eval_expression(), 2)
        self.assertEqual(XPath("(4 + 3 * 5)").eval_expression(), 19)
        self.assertEqual(XPath("(4 + 3 * 5) - 9").eval_expression(), 10)
        self.assertEqual(
            XPath("(1 + 2 * 3 - 4 div 5 * 6 - 7) * (3 - 5)").eval_expression(),
            9.600000000000001,
        )

    def test_calculations_variables(self):
        variable_map = {
            "var_to_list": [1, 5, 3],
            "var_to_value": 9,
            "var_to_value_max": 5,
            "var_to_value_min": 1,
            "var_to_value_count": 3,
            "var_to_value_avg": 3,
        }
        xpath_sum = XPath(
            "+ sum($var_to_list) = $var_to_value", variable_map=variable_map
        )
        # Loops though parsed resultes, resolves qnames from variable map
        xpath_sum.resolve_qnames()
        # Evaluate the expression
        self.assertTrue(xpath_sum.eval_expression())

        xpath_max = XPath(
            "max($var_to_list) = $var_to_value_max", variable_map=variable_map
        )
        # Loops though parsed resultes, resolves qnames from variable map
        xpath_max.resolve_qnames()
        # Evaluate the expression
        self.assertTrue(xpath_max.eval_expression())

        xpath_min = XPath(
            "min($var_to_list) = $var_to_value_min", variable_map=variable_map
        )
        # Loops though parsed resultes, resolves qnames from variable map
        xpath_min.resolve_qnames()
        # Evaluate the expression
        self.assertTrue(xpath_min.eval_expression())

        xpath_count = XPath(
            "count($var_to_list) = $var_to_value_count", variable_map=variable_map
        )
        # Loops though parsed resultes, resolves qnames from variable map
        xpath_count.resolve_qnames()
        # Evaluate the expression
        self.assertTrue(xpath_count.eval_expression())

        xpath_avg = XPath(
            "avg($var_to_list) = $var_to_value_avg", variable_map=variable_map
        )
        # Loops though parsed resultes, resolves qnames from variable map
        xpath_avg.resolve_qnames()
        # Evaluate the expression
        self.assertTrue(xpath_avg.eval_expression())
