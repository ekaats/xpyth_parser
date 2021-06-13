
import unittest

from conversion.functions.aggregate import Count, Avg, Max, Min, Sum
from conversion.qname import QName
from conversion.tests import Test
from grammar.expressions import t_XPath


class FunctionsOperatorsSequences(unittest.TestCase):
    """
    Functions and operators on sequences
    https://www.w3.org/TR/xpath-functions/#sequence-functions
    """


    def test_aggregate_functions(self):

        # Parse a string using Pyparsing
        count = t_XPath.parseString("count(1,2,3)", parseAll=True)[0]

        # This returns a Python function which can be used elsewhere
        # The function contains the QName which identifies the function, as well as the arguments
        self.assertEqual(count, Count(qname=QName(localname="count"), arguments=(1,2,3)))

        # Functions can have a run() function which returns a value as described in the Xpath functions document
        #  (e.g., https://www.w3.org/TR/xpath-functions/#func-count)
        self.assertEqual(count.run(), 3)

        avg = t_XPath.parseString("avg(1,4,2,3,12,3,6)", parseAll=True)[0]
        self.assertEqual(avg, Avg(qname=QName(localname="avg"), arguments=(1,4,2,3,12,3,6)))
        self.assertEqual(avg.run(), 4.428571428571429)

        max = t_XPath.parseString("max(1,4,2,3,12,3,6)", parseAll=True)[0]
        self.assertEqual(max, Max(qname=QName(localname="max"), arguments=(1,4,2,3,12,3,6)))
        self.assertEqual(max.run(), 12)

        min = t_XPath.parseString("min(4,2,3,12,3,6)", parseAll=True)[0]
        self.assertEqual(min, Min(qname=QName(localname="min"), arguments=(4,2,3,12,3,6)))
        self.assertEqual(min.run(), 2)

        sum = t_XPath.parseString("sum(1,4,2,3,12,3,6)", parseAll=True)[0]
        self.assertEqual(sum, Sum(qname=QName(localname="sum"), arguments=(1,4,2,3,12,3,6)))
        self.assertEqual(sum.run(), 31)




