
import unittest

from src.xpyth_parser.conversion.functions.aggregate import Count, Avg, Max, Min, Sum
from src.xpyth_parser.conversion.qname import QName
from src.xpyth_parser.parse import XPath


class FunctionsOperatorsSequences(unittest.TestCase):
    """
    Functions and operators on sequences
    https://www.w3.org/TR/xpath-functions/#sequence-functions
    """


    def test_aggregate_functions(self):

        # Parse a string using Pyparsing
        count = XPath.parseString("count(1,2,3)", parseAll=True)[0]

        # This returns a Python function which can be used elsewhere
        # The function contains the QName which identifies the function, as well as the arguments
        self.assertEqual(count, Count(qname=QName(prefix="fn", localname="count"), arguments=(1,2,3)))

        # Functions can have a run() function which returns a value as described in the Xpath functions document
        #  (e.g., https://www.w3.org/TR/xpath-functions/#func-count)
        self.assertEqual(count.run(), 3)

        avg = XPath.parseString("avg(1,4,2,3,12,3,6)", parseAll=True)[0]
        self.assertEqual(avg, Avg(qname=QName(prefix="fn", localname="avg"), arguments=(1,4,2,3,12,3,6)))
        self.assertEqual(avg.run(), 4.428571428571429)

        max = XPath.parseString("max(1,4,2,3,12,3,6)", parseAll=True)[0]
        self.assertEqual(max, Max(qname=QName(prefix="fn", localname="max"), arguments=(1,4,2,3,12,3,6)))
        self.assertEqual(max.run(), 12)

        min = XPath.parseString("min(4,2,3,12,3,6)", parseAll=True)[0]
        self.assertEqual(min, Min(qname=QName(prefix="fn", localname="min"), arguments=(4,2,3,12,3,6)))
        self.assertEqual(min.run(), 2)

        sum = XPath.parseString("sum(1,4,2,3,12,3,6)", parseAll=True)[0]
        self.assertEqual(sum, Sum(qname=QName(prefix="fn", localname="sum"), arguments=(1,4,2,3,12,3,6)))
        self.assertEqual(sum.run(), 31)
