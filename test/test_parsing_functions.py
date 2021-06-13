
import unittest

from conversion.function import Function, Count
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


