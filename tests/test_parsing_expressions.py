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
from src.xpyth_parser.parse import Parser


class ExpressionTests(unittest.TestCase):
    def test_expressions(self):
        """
        Run tests which validate simple expressions

        :return:
        """
        # Var ref
        self.assertEqual(
            list(t_XPath.parseString("var:ref", parseAll=True))[0].expr,
            QName(prefix="var", localname="ref"),
        )

        l1 = list(t_AdditiveExpr.parseString("1 + 2", parseAll=True))
        self.assertEqual(l1[0].left.value, 1)
        self.assertTrue(isinstance(l1[0].op, ast.Add))
        self.assertEqual(l1[0].right.value, 2)

        # Parenthesized Expression becomes a XPath expression object
        l2 = list(t_ParenthesizedExpr.parseString("(1 + 2)", parseAll=True))
        self.assertEqual(l2[0].expr.left.value, 1)
        self.assertTrue(isinstance(l2[0].expr.op, ast.Add))
        self.assertEqual(l2[0].expr.right.value, 2)

        l3 = list(t_XPath.parseString("(1 + 2 * 3) * (3 - 5)", parseAll=True))[0].expr
        self.assertEqual(l3.left.expr.left.value, 1)
        self.assertTrue(isinstance(l3.left.expr.op, ast.Add))

        self.assertEqual(l3.left.expr.right.left.value, 2)
        self.assertTrue(isinstance(l3.left.expr.right.op, ast.Mult))
        self.assertEqual(l3.left.expr.right.right.value, 3)

        self.assertTrue(isinstance(l3.op, ast.Mult))
        self.assertEqual(l3.right.expr.left.value, 3)
        self.assertTrue(isinstance(l3.right.expr.op, ast.Sub))
        self.assertEqual(l3.right.expr.right.value, 5)

        l4 = list(t_XPath.parseString("(2 + localname)", parseAll=True))[0].expr
        self.assertEqual(l4.expr.left.value, 2)
        self.assertTrue(isinstance(l4.expr.op, ast.Add))
        self.assertEqual(l4.expr.right, QName(localname="localname"))

        # Context Item Expression
        self.assertEqual(list(t_PrimaryExpr.parseString(".", parseAll=True)), ["."])

        # Function Call
        l6 = list(t_PrimaryExpr.parseString("my:function(1,2)", parseAll=True))
        self.assertTrue(isinstance(l6[0], Function))
        self.assertEqual(l6[0].qname, QName(prefix="my", localname="function"))
        self.assertEqual(l6[0].arguments[0].value, 1)
        self.assertEqual(l6[0].arguments[1].value, 2)

    def test_operators(self):
        """
        Test operative expressions
        """
        l1 = list(t_UnaryExpr.parseString(f"+ 1", parseAll=True))
        self.assertTrue(isinstance(l1[0], ast.UnaryOp))
        self.assertTrue(isinstance(l1[0].op, ast.UAdd))
        self.assertEqual(l1[0].operand.value, 1)

        l2 = list(t_XPath.parseString(f"+ 1", parseAll=True))[0].expr
        self.assertTrue(isinstance(l2, ast.UnaryOp))
        self.assertTrue(isinstance(l2.op, ast.UAdd))
        self.assertEqual(l2.operand.value, 1)

        l3 = list(t_UnaryExpr.parseString("+ (1 + 2)", parseAll=True))[0]
        self.assertTrue(isinstance(l3, ast.UnaryOp))
        self.assertTrue(isinstance(l3.op, ast.UAdd))

        self.assertTrue(isinstance(l3.operand.expr, ast.BinOp))
        self.assertEqual(l3.operand.expr.left.value, 1)
        self.assertTrue(isinstance(l3.operand.expr.op, ast.Add))
        self.assertEqual(l3.operand.expr.right.value, 2)

        l4 = Parser("+ sum(1,3)", parseAll=True, no_resolve=True).XPath
        self.assertTrue(isinstance(l4.expr, ast.UnaryOp))
        self.assertTrue(isinstance(l4.expr.op, ast.UAdd))
        # The unary expression before a function should parse correctly

        self.assertTrue(isinstance(l4.expr.operand, Function))
        self.assertEqual(l4.expr.operand.qname, QName(prefix="fn", localname="sum"))
        self.assertEqual(l4.expr.operand.arguments[0].value, 1)
        self.assertEqual(l4.expr.operand.arguments[1].value, 3)

    def test_compile_arithmetic(self):

        self.assertEqual(Parser("1 + 2").run(), 3)
        self.assertEqual(Parser("(3 - 5)").run(), -2)
        self.assertEqual(Parser("(4 + 3 - 5)").run(), 2)
        self.assertEqual(Parser("(4 + 3 * 5)").run(), 19)
        self.assertEqual(Parser("(4 + 3 * 5) - 9").run(), 10)
        self.assertEqual(
            Parser("(1 + 2 * 3 - 4 div 5 * 6 - 7) * (3 - 5)").run(),
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
        xpath_sum = Parser(
            "+ sum($var_to_list) = $var_to_value", variable_map=variable_map
        )
        # Loops though parsed resultes, resolves qnames from variable map
        # xpath_sum.resolve_expression()
        # Evaluate the expression
        self.assertTrue(xpath_sum.run())

        xpath_max = Parser(
            "max($var_to_list) = $var_to_value_max", variable_map=variable_map
        )
        # Loops though parsed resultes, resolves qnames from variable map
        # xpath_max.resolve_expression()
        # Evaluate the expression
        self.assertTrue(xpath_max.run())

        xpath_min = Parser(
            "min($var_to_list) = $var_to_value_min", variable_map=variable_map
        )
        # Loops though parsed resultes, resolves qnames from variable map
        # xpath_min.resolve_expression()
        # Evaluate the expression
        self.assertTrue(xpath_min.run())

        xpath_count = Parser(
            "count($var_to_list) = $var_to_value_count", variable_map=variable_map
        )
        # Loops though parsed resultes, resolves qnames from variable map
        # xpath_count.resolve_expression()
        # Evaluate the expression
        self.assertTrue(xpath_count.run())

        xpath_avg = Parser(
            "avg($var_to_list) = $var_to_value_avg", variable_map=variable_map
        )
        # Loops though parsed resultes, resolves qnames from variable map
        # xpath_avg.resolve_expression()
        # Evaluate the expression
        self.assertTrue(xpath_avg.run())

    def test_if_expressions(self):
        direct_xpath = t_XPath.parseString("if(1 = 1) then a else b", parseAll=True)[0]

        self.assertEqual(direct_xpath.expr.test_expr.expr.left.value, 1)
        self.assertEqual(direct_xpath.expr.test_expr.expr.comparators[0].value, 1)
        self.assertTrue(isinstance(direct_xpath.expr.test_expr.expr.ops[0], ast.Eq))
        self.assertEqual(direct_xpath.expr.then_expr, QName(localname="a"))
        self.assertEqual(direct_xpath.expr.else_expr, QName(localname="b"))

        # With the parser, the answer is automatically given.
        self.assertEqual(
            Parser("if(1 = 1) then a else b").XPath.expr, QName(localname="a")
        )
        self.assertEqual(
            Parser("if(1 = 1) then a else b").XPath.expr, QName(localname="a")
        )

        # Or the shorthand, get_outcome
        self.assertEqual(
            Parser("if(1 = 1) then a else b").get_outcome(), QName(localname="a")
        )
        self.assertEqual(
            Parser("if(1 = 2) then a else b").get_outcome(), QName(localname="b")
        )
