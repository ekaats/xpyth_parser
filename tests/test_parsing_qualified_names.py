import unittest

from pyparsing import ParseException

from src.conversion.qname import QName
from src.grammar.qualified_names import t_QName, t_VarName, t_Wildcard


class QualifiedNameTests(unittest.TestCase):

    def test_qualified_names(self):
        # Prefix
        self.assertEqual(list(t_QName.parseString("localname", parseAll=True)), [QName(localname='localname')])
        self.assertEqual(list(t_QName.parseString("T3st", parseAll=True)), [QName(localname='T3st')])



        #QName
        self.assertEqual(list(t_QName.parseString("prefix:localname", parseAll=True)),
                         [QName(prefix="prefix", localname='localname')])
        self.assertEqual(list(t_QName.parseString("localname", parseAll=True)),
                         [QName(localname='localname')])
        self.assertEqual(list(t_VarName.parseString("prefix:localname", parseAll=True)),
                         [QName(prefix="prefix", localname='localname')])
        self.assertEqual(list(t_VarName.parseString("localname", parseAll=True)),
                         [QName(localname='localname')])
        self.assertEqual(list(t_VarName.parseString("xyz:function-with-minus-sign", parseAll=True)),
                         [QName(prefix="xyz", localname="function-with-minus-sign")])
        self.assertEqual(list(t_VarName.parseString("function-with-minus-sign", parseAll=True)),
                         [QName(localname="function-with-minus-sign")])

        # Do not allow QName with colon, but no prefix or localname. Also do not allow qname with a wildcard
        self.assertRaises(ParseException, t_QName.parseString, "prefix:", parseAll=True)
        self.assertRaises(ParseException, t_QName.parseString, "prefix:*", parseAll=True)
        self.assertRaises(ParseException, t_QName.parseString, ":localname", parseAll=True)
        self.assertRaises(ParseException, t_QName.parseString, "*:localname", parseAll=True)

        #Wildcards
        self.assertEqual(list(t_Wildcard.parseString("*:localname", parseAll=True)), ['*', ':', 'localname'])
        self.assertEqual(list(t_Wildcard.parseString("prefix:*", parseAll=True)), ['prefix', ':', "*"])
