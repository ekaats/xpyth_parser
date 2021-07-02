import unittest
from pyparsing import ParseException

from src.grammar.expressions import t_PrimaryExpr
from src.grammar.literals import t_IntegerLiteral, t_DecimalLiteral, t_DoubleLiteral, t_NumericLiteral, t_StringLiteral, \
    t_Char, t_NameStartChar, t_NCName, t_NameChar


class TestLiterals(unittest.TestCase):

    def test_numeric_literals(self):
        """
        Run tests for Integer, Decimal and Numeric literals
        """

        # Test directly
        self.assertEqual(list(t_IntegerLiteral.parseString("4362", parseAll=True)), [4362])
        self.assertEqual(list(t_DecimalLiteral.parseString("4362.21", parseAll=True)), [float(4362.21)])
        self.assertEqual(list(t_DoubleLiteral.parseString(".42", parseAll=True)), [float(.42)])
        self.assertEqual(list(t_DoubleLiteral.parseString("4362.21e-3", parseAll=True)), [float(4362.21e-3)])
        self.assertEqual(list(t_DoubleLiteral.parseString("4362.21e4", parseAll=True)), [float(4362.21e4)])

        # Test via NumericLiteral
        self.assertEqual(list(t_NumericLiteral.parseString("4362", parseAll=True)), [4362])
        self.assertEqual(list(t_NumericLiteral.parseString("4362.21", parseAll=True)), [float(4362.21)])
        self.assertEqual(list(t_NumericLiteral.parseString(".42", parseAll=True)), [float(.42)])
        self.assertEqual(list(t_NumericLiteral.parseString("4362.21e-3", parseAll=True)), [float(4362.21e-3)])

    def test_char_literals(self):
        """
        Run NameChar literal and other character specific tests
        """
        self.assertEqual(list(t_StringLiteral.parseString("'test'", parseAll=True)), ["test"])
        self.assertEqual(list(t_StringLiteral.parseString('"String"', parseAll=True)), ["String"])

        # Todo: Add some exotic char checks
        # Char tests
        self.assertEqual(list(t_Char.parseString("a", parseAll=True)), ['a'])
        self.assertEqual(list(t_Char.parseString("Q", parseAll=True)), ['Q'])

        self.assertEqual(list(t_NameStartChar.parseString("a", parseAll=True)), ['a'])
        self.assertEqual(list(t_NameStartChar.parseString("Q", parseAll=True)), ['Q'])
        self.assertEqual(list(t_NameChar.parseString("-", parseAll=True)), ["-"])
        self.assertEqual(list(t_NCName.parseString("function-with-minus-sign", parseAll=True)), ["function-with-minus-sign"])


        self.assertEqual(list(t_NCName.parseString("T3st", parseAll=True)), ['T3st'])
        # The next test should fail as the colon is not allowed
        self.assertRaises(ParseException, t_NCName.parseString, "T3st:ds", parseAll=True)

    def test_string_literals(self):
        """
        Run tests on string literals
        """


        # (String) literal
        self.assertEqual(list(t_PrimaryExpr.parseString("'String literal'", parseAll=True)), ["String literal"])