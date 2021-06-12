import unittest

from conversion.calculation import Calculation
from conversion.function import Function
from conversion.qname import QName

from grammar.expressions import t_PrimaryExpr, t_UnaryExpr, t_AdditiveExpr, t_XPath, t_ComparisonExpr, \
    t_ParenthesizedExpr


class ExpressionTests(unittest.TestCase):



    def test_expressions(self):


        # (String) literal
        self.assertEqual(list(t_PrimaryExpr.parseString("'String literal'", parseAll=True)), ["String literal"])

        # Var ref
        # self.assertEqual(list(t_PrimaryExpr.parseString("var:ref", parseAll=True)), [QName(prefix="var", localname='ref')])

        # Parenthesized Expression

        self.assertEqual(list(t_AdditiveExpr.parseString("1 + 2", parseAll=True)), [1, "+", 2])
        # self.assertEqual(list(t_ParenthesizedExpr.parseString("(1 + 2)", parseAll=True)),
        #                  [Calculation(operator="+", value_1=1, value_2=2)])
        self.assertEqual(list(t_ParenthesizedExpr.parseString("(1 + 2)", parseAll=True)),
                         [1, "+", 2])

        self.assertEqual(list(t_XPath.parseString("(1 + 2 + 3) * (3 - 5)", parseAll=True)),
                         [(1, "+", 2, "+", 3), "*", (3, "-", 5,)])
        self.assertEqual(list(t_XPath.parseString("(1 + 2 + localname) * (3 - 5)", parseAll=True)),
                         [(1, "+", 2, "+", QName(localname="localname")), "*", (3, "-", 5)])

        # self.assertEqual(list(t_XPath.parseString("(1 + localname) - (3 + 5)", parseAll=True)),
        #                  [Calculation(operator="-",
        #                               value_1=Calculation(operator="+", value_1=1, value_2=QName(localname="localname")),
        #                               value_2=Calculation(operator="+", value_1=3, value_2=5)
        #                               )
        #                   ])
        # self.assertEqual(list(t_XPath.parseString("(1 + localname) - (3 + 5)", parseAll=True)),
        #                  [Calculation(operator="-",
        #                               value_1=Calculation(operator="+", value_1=1, value_2=QName(localname="localname")),
        #                               value_2=Calculation(operator="+", value_1=3, value_2=5)
        #                               )
        #                   ])
        #
        #
        # self.assertEqual(list(t_XPath.parseString("(1 * 2 - (3 + 5)) * 2", parseAll=True)),
        #                  [Calculation(operator="-",
        #                               value_1=Calculation(operator="+", value_1=1, value_2=QName(localname="localname")),
        #                               value_2=Calculation(operator="+", value_1=3, value_2=5)
        #                               )
        #                   ])

        # Context Item Expression
        self.assertEqual(list(t_PrimaryExpr.parseString(".", parseAll=True)), ["."])

        # Function Call
        # self.assertEqual(list(t_PrimaryExpr.parseString("my:function(1,2)", parseAll=True)),
        #                  [QName(prefix="my", localname='function'), 1, ',', 2])
        self.assertEqual(list(t_PrimaryExpr.parseString("my:function(1,2)", parseAll=True)),
                         [Function(arguments=[1, 2])])


    def test_operators(self):
        self.assertEqual(list(t_UnaryExpr.parseString(f"+ 1", parseAll=True)), ["+", 1])
        # self.assertEqual(list(t_UnaryExpr.parseString(f" - localname", parseAll=True)), ["-", QName(localname="localname")])
        self.assertEqual(list(t_UnaryExpr.parseString("+ ()", parseAll=True)), ["+", ()])

        # Additive Expressions
        self.assertEqual(list(t_AdditiveExpr.parseString("1 + 1", parseAll=True)), [1, "+", 1])

    #
    # def test_test(self):
    #     test = t_PrimaryExpr.parseString("(1 + 2)", parseAll=True)
    #     print(test)
    #     unpacked = list(test)
    #     print(unpacked)

if __name__ == '__main__':
    unittest.main()