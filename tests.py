import unittest
import grammar as gr
from conversion.qname import QName

from pyparsing import ParseException


class XPath_parser_tests(unittest.TestCase):

    def test_numeric_literals(self):
        """
        Tests if the most primitive parts of the parser work
        """

        # Test directly
        self.assertEqual(list(gr.t_IntegerLiteral.parseString("4362", parseAll=True)), [4362])
        self.assertEqual(list(gr.t_DecimalLiteral.parseString("4362.21", parseAll=True)), [float(4362.21)])
        self.assertEqual(list(gr.t_DoubleLiteral.parseString(".42", parseAll=True)), [float(.42)])
        self.assertEqual(list(gr.t_DoubleLiteral.parseString("4362.21e-3", parseAll=True)), [float(4362.21e-3)])
        self.assertEqual(list(gr.t_DoubleLiteral.parseString("4362.21e4", parseAll=True)), [float(4362.21e4)])

        # Test via NumericLiteral
        self.assertEqual(list(gr.t_NumericLiteral.parseString("4362", parseAll=True)), [4362])
        self.assertEqual(list(gr.t_NumericLiteral.parseString("4362.21", parseAll=True)), [float(4362.21)])
        self.assertEqual(list(gr.t_NumericLiteral.parseString(".42", parseAll=True)), [float(.42)])
        self.assertEqual(list(gr.t_NumericLiteral.parseString("4362.21e-3", parseAll=True)), [float(4362.21e-3)])

    def test_char_literals(self):
        """
        Test the other kind of literals and chars
        """
        self.assertEqual(list(gr.t_StringLiteral.parseString("'test'", parseAll=True)), ["test"])
        self.assertEqual(list(gr.t_StringLiteral.parseString('"String"', parseAll=True)), ["String"])
        # self.assertEqual(list(gr.t_StringLiteral.parseString("Test String", parseAll=True)), ['Test', 'String'])

        # Todo: Add some exotic char checks
        # Char tests
        self.assertEqual(list(gr.t_Char.parseString("a", parseAll=True)), ['a'])
        self.assertEqual(list(gr.t_Char.parseString("Q", parseAll=True)), ['Q'])

        self.assertEqual(list(gr.t_NameStartChar.parseString("a", parseAll=True)), ['a'])
        self.assertEqual(list(gr.t_NameStartChar.parseString("Q", parseAll=True)), ['Q'])

        # Prefix
        self.assertEqual(list(gr.t_QName.parseString("localname", parseAll=True)), [QName(localname='localname')])
        self.assertEqual(list(gr.t_QName.parseString("T3st", parseAll=True)), [QName(localname='T3st')])

        # The next test should fail as the colon is not allowed
        self.assertRaises(ParseException, gr.t_NCName.parseString, "T3st:ds", parseAll=True)
        self.assertEqual(list(gr.t_NCName.parseString("T3st", parseAll=True)), ['T3st'])

        #QName
        self.assertEqual(list(gr.t_QName.parseString("prefix:localname", parseAll=True)),
                         [QName(prefix="prefix", localname='localname')])
        self.assertEqual(list(gr.t_QName.parseString("localname", parseAll=True)),
                         [QName(localname='localname')])
        self.assertEqual(list(gr.t_VarName.parseString("prefix:localname", parseAll=True)),
                         [QName(prefix="prefix", localname='localname')])
        self.assertEqual(list(gr.t_VarName.parseString("localname", parseAll=True)),
                         [QName(localname='localname')])

        # Do not allow QName with colon, but no prefix or localname. Also do not allow qname with a wildcard
        self.assertRaises(ParseException, gr.t_QName.parseString, "prefix:", parseAll=True)
        self.assertRaises(ParseException, gr.t_QName.parseString, "prefix:*", parseAll=True)
        self.assertRaises(ParseException, gr.t_QName.parseString, ":localname", parseAll=True)
        self.assertRaises(ParseException, gr.t_QName.parseString, "*:localname", parseAll=True)

        #Wildcards
        self.assertEqual(list(gr.t_Wildcard.parseString("*:localname", parseAll=True)), ['*', ':', 'localname'])
        self.assertEqual(list(gr.t_Wildcard.parseString("prefix:*", parseAll=True)), ['prefix', ':', "*"])

    def test_kind_tests(self):
        # Empty document-node
        self.assertEqual(list(gr.t_KindTest.parseString(f"document-node()", parseAll=True)),[f"document-node", "(", ")"])

        # Empty element test
        self.assertEqual(list(gr.t_KindTest.parseString(f"element()", parseAll=True)), [f"element", "(", ")"])

        # document-node with element test
        self.assertEqual(list(gr.t_KindTest.parseString(f"document-node(element())", parseAll=True)),
                         [f"document-node", "(","element", "(", ")", ")"])

        # Empty attribute test
        self.assertEqual(list(gr.t_KindTest.parseString(f"attribute()", parseAll=True)), [f"attribute", "(", ")"])

        # Schema-element test
        self.assertEqual(list(gr.t_KindTest.parseString(f"schema-element(px:name)", parseAll=True)),
                         [f"schema-element", "(", QName(prefix="px", localname='name'), ")"])

        # Schema-element test
        self.assertEqual(list(gr.t_KindTest.parseString(f"schema-attribute(px:name)", parseAll=True)),
                         [f"schema-attribute", "(", QName(prefix="px", localname='name'), ")"])

        # empty processing-instruction test
        self.assertEqual(list(gr.t_KindTest.parseString(f"processing-instruction()", parseAll=True)),
                         [f"processing-instruction", "(", ")"])

        # empty comment, test and node test
        for keyword in ["comment", "text", "node"]:
            self.assertEqual(list(gr.t_KindTest.parseString(f"{keyword}()", parseAll=True)),[f"{keyword}", "(", ")"])

    def test_predicates(self):
        self.assertEqual(list(gr.t_PredicateList.parseString("", parseAll=True)), [])
        self.assertEqual(list(gr.t_PredicateList.parseString("[1]", parseAll=True)), ["[", 1, "]"])



    def test_path_expressions(self):
        for keyword in ["child", "descendant", "attribute", "self", "descendant-or-self", "following-sibling", "following", "namespace"]:
            self.assertEqual(list(gr.t_ForwardAxis.parseString(f"{keyword}::", parseAll=True)), [f"{keyword}", "::"])
            self.assertEqual(list(gr.t_ForwardAxis.parseString(f"{keyword} ::", parseAll=True)), [f"{keyword}", "::"])

        for keyword in ["ancestor", "preceding-sibling", "preceding", "ancestor-or-self", "parent"]:
            self.assertEqual(list(gr.t_ReverseAxis.parseString(f"{keyword}::", parseAll=True)), [f"{keyword}", "::"])
            self.assertEqual(list(gr.t_ReverseAxis.parseString(f"{keyword} ::", parseAll=True)), [f"{keyword}", "::"])

        # With an element test
        self.assertEqual(list(gr.t_ForwardStep.parseString(f"following-sibling::element(*)", parseAll=True)),
                         [f"following-sibling", "::", "element", "(", "*", ")"])
        self.assertEqual(list(gr.t_ReverseStep.parseString(f"ancestor-or-self::element(*)", parseAll=True)),
                         [f"ancestor-or-self", "::", "element", "(", "*", ")"])

        self.assertEqual(list(gr.t_ForwardStep.parseString(f"descendant::prefix:localname", parseAll=True)),
                         [f"descendant", "::", QName(prefix="prefix", localname='localname')])

        self.assertEqual(list(gr.t_ReverseStep.parseString(f"preceding-sibling::prefix:localname", parseAll=True)),
                         [f"preceding-sibling", "::", QName(prefix="prefix", localname='localname')])

    def test_expressions(self):
        #todo: figure out for loops
        # and exprSingle. The documentation of that part is a bit strange.



        # testthingy = gr.t_SimpleForClause.parseString(
        #     "for $a in fn:distinct-values(book/author) return (book/author[. = $a][1], book[author = $a]/title)")
        # testthingy = gr.t_SimpleForClause.parseString("for $f in prefix:test return $y")
        # testthingy = gr.t_IfExpr.parseString("if (prefix:test < test2) then $outcome1 else $outcome2")
        # self.assertEqual(list(gr.t_UnaryExpr.parseString("+", parseAll=True)), ["+"])

        # (String) literal
        self.assertEqual(list(gr.t_PrimaryExpr.parseString("'String literal'", parseAll=True)), ["String literal"])
        # Var ref
        self.assertEqual(list(gr.t_PrimaryExpr.parseString("var:ref", parseAll=True)),
                         [QName(prefix="var", localname='ref')])
        # Parentisized Expression
        # self.assertEqual(list(gr.t_PrimaryExpr.parseString("(1 + 1)", parseAll=True)), ["1", "+", "1"])
        # Context Item Expression
        self.assertEqual(list(gr.t_PrimaryExpr.parseString(".", parseAll=True)), ["."])
        # Function Call
        self.assertEqual(list(gr.t_PrimaryExpr.parseString("my:function(1,2)", parseAll=True)),
                         [QName(prefix="my", localname='function'), '(', 1, ',', 2, ')'])


        pass

if __name__ == '__main__':
    unittest.main()