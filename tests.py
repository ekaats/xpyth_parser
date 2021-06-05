import unittest
import grammar as gr

from pyparsing import ParseException


class XPath_parser_tests(unittest.TestCase):

    def test_numeric_literals(self):
        """
        Tests if the most primitive parts of the parser work
        """

        # Test directly
        self.assertEqual(list(gr.t_IntegerLiteral.parseString("4362", parseAll=True)), ['4362'])
        self.assertEqual(list(gr.t_DecimalLiteral.parseString("4362.21", parseAll=True)), ['4362', '.', '21'])
        self.assertEqual(list(gr.t_DoubleLiteral.parseString(".42", parseAll=True)), ['.', '42'])
        self.assertEqual(list(gr.t_DoubleLiteral.parseString("4362.21e-3", parseAll=True)), ['4362', '.', '21', 'e', '-', '3'])

        # Test via NumericLiteral
        self.assertEqual(list(gr.t_NumericLiteral.parseString("4362", parseAll=True)), ['4362'])
        self.assertEqual(list(gr.t_NumericLiteral.parseString("4362.21", parseAll=True)), ['4362', '.', '21'])
        self.assertEqual(list(gr.t_NumericLiteral.parseString(".42", parseAll=True)), ['.', '42'])
        self.assertEqual(list(gr.t_NumericLiteral.parseString("4362.21e-3", parseAll=True)), ['4362', '.', '21', 'e', '-', '3'])

    def test_char_literals(self):
        """
        Test the other kind of literals and chars
        """
        self.assertEqual(list(gr.t_StringLiteral.parseString("test", parseAll=True)), ['test'])
        self.assertEqual(list(gr.t_StringLiteral.parseString("String", parseAll=True)), ['String'])
        # self.assertEqual(list(gr.t_StringLiteral.parseString("Test String", parseAll=True)), ['Test', 'String'])

        # Char tests
        self.assertEqual(list(gr.t_Char.parseString("a", parseAll=True)), ['a'])
        self.assertEqual(list(gr.t_Char.parseString("Q", parseAll=True)), ['Q'])

        self.assertEqual(list(gr.t_NameStartChar.parseString("a", parseAll=True)), ['a'])
        self.assertEqual(list(gr.t_NameStartChar.parseString("Q", parseAll=True)), ['Q'])

        # Prefix
        self.assertEqual(list(gr.t_Name.parseString("prefix", parseAll=True)), ['prefix'])
        self.assertEqual(list(gr.t_Name.parseString("T3st", parseAll=True)), ['T3st'])

        # The next test should fail as the colon is not allowed
        self.assertRaises(ParseException, gr.t_NCName.parseString, "T3st:ds", parseAll=True)
        self.assertEqual(list(gr.t_NCName.parseString("T3st", parseAll=True)), ['T3st'])

if __name__ == '__main__':
    unittest.main()