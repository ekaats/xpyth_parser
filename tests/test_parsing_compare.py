import unittest
import ast
from src.xpyth_parser.parse import XPath


class ComparisonTests(unittest.TestCase):
    def test_general_comparisons(self):
        """
        Test operative expressions

        Keyword("=") | Keyword("!=") | Keyword("<") | Keyword("<=") | Keyword(">") | Keyword(">=")
        """
        l1 = XPath(f"1 = 1")

        self.assertTrue(isinstance(l1.XPath[0], ast.Compare))
        self.assertEqual(l1.XPath[0].left.value, 1)
        self.assertTrue(isinstance(l1.XPath[0].ops[0], ast.Eq))
        self.assertEqual(l1.XPath[0].comparators[0].value, 1)

        self.assertTrue(XPath(f"1 = 1").eval_expression())
        self.assertFalse(XPath(f"1 = 2").eval_expression())
        self.assertTrue(XPath(f"1 != 2").eval_expression())
        self.assertFalse(XPath(f"1 != 1").eval_expression())

        self.assertTrue(XPath(f"1 != (1 + 1)").eval_expression())
        self.assertTrue(XPath(f"(1 + 2) != (1 + 1)").eval_expression())
        self.assertTrue(XPath(f"2 = (1 + 1)").eval_expression())
        self.assertTrue(XPath(f"(1 + 2) = (2 + 1)").eval_expression())
