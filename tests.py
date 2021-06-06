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
        self.assertEqual(list(gr.t_StringLiteral.parseString("'test'", parseAll=True)), ["'test'"])
        self.assertEqual(list(gr.t_StringLiteral.parseString('"String"', parseAll=True)), ['"String"'])
        # self.assertEqual(list(gr.t_StringLiteral.parseString("Test String", parseAll=True)), ['Test', 'String'])

        # Todo: Add some exotic char checks
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

        #QName
        self.assertEqual(list(gr.t_QName.parseString("prefix:localname", parseAll=True)), ['prefix', ':', 'localname'])
        self.assertEqual(list(gr.t_QName.parseString("localname", parseAll=True)), ['localname'])
        self.assertEqual(list(gr.t_VarName.parseString("prefix:localname", parseAll=True)), ['prefix', ':', 'localname'])
        self.assertEqual(list(gr.t_VarName.parseString("localname", parseAll=True)), ['localname'])

        # Do not allow QName with colon, but no prefix or localname. Also not with a wildcard
        self.assertRaises(ParseException, gr.t_QName.parseString, "prefix:", parseAll=True)
        self.assertRaises(ParseException, gr.t_QName.parseString, "prefix:*", parseAll=True)
        self.assertRaises(ParseException, gr.t_QName.parseString, ":localname", parseAll=True)
        self.assertRaises(ParseException, gr.t_QName.parseString, "*:localname", parseAll=True)

        #Wildcards
        self.assertEqual(list(gr.t_Wildcard.parseString("*:localname", parseAll=True)), ['*', ':', 'localname'])
        self.assertEqual(list(gr.t_Wildcard.parseString("prefix:*", parseAll=True)), ['prefix', ':', "*"])

    def test_expressions(self):
        #todo: figure out for loops
        # and exprSingle. The documentation of that part is a bit strange.

        # testthingy = gr.t_SimpleForClause.parseString(
        #     "for $a in fn:distinct-values(book/author) return (book/author[. = $a][1], book[author = $a]/title)")
        # testthingy = gr.t_SimpleForClause.parseString("for $f in prefix:test return $y")
        # testthingy = gr.t_IfExpr.parseString("if (prefix:test < test2) then $outcome1 else $outcome2")
        # (String) literal
        self.assertEqual(list(gr.t_PrimaryExpr.parseString("'String literal'", parseAll=True)), ["'String literal'"])
        # Var ref
        self.assertEqual(list(gr.t_PrimaryExpr.parseString("var:ref", parseAll=True)), ["var", ":", "ref"])
        # Parentisized Expression
        # self.assertEqual(list(gr.t_PrimaryExpr.parseString("(1 + 1)", parseAll=True)), ["1", "+", "1"])
        # Context Item Expression
        self.assertEqual(list(gr.t_PrimaryExpr.parseString(".", parseAll=True)), ["."])
        # Function Call
        self.assertEqual(list(gr.t_PrimaryExpr.parseString("my:function(1,2)", parseAll=True)), ['my', ':', 'function', '(', '1', ',', '2', ')'])


        pass

if __name__ == '__main__':
    unittest.main()