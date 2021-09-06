import unittest
import operator

from src.xpyth_parser.conversion.calculation import Compare
from src.xpyth_parser.parse import Parser


class ComparisonTests(unittest.TestCase):
    def test_general_comparisons(self):
        """
        Test operative expressions

        Keyword("=") | Keyword("!=") | Keyword("<") | Keyword("<=") | Keyword(">") | Keyword(">=")
        """
        l1 = Parser(f"1 = 1", no_resolve=True)

        self.assertTrue(isinstance(l1.XPath.expr, Compare))
        self.assertEqual(l1.XPath.expr.left, 1)
        self.assertEqual(l1.XPath.expr.comparators[0], 1)

        self.assertTrue(Parser(f"1 = 1").run())
        self.assertFalse(Parser(f"1 = 2").run())
        self.assertTrue(Parser(f"1 != 2").run())
        self.assertFalse(Parser(f"1 != 1").run())

        self.assertTrue(Parser(f"1 != (1 + 1)").run())
        self.assertTrue(Parser(f"(1 + 2) != (1 + 1)").run())
        self.assertTrue(Parser(f"2 = (1 + 1)").run())  # General comparison
        self.assertTrue(Parser(f"2 eq (1 + 1)").run())  # Value comparison
        self.assertTrue(Parser(f"(1 + 2) = (2 + 1)").run())
