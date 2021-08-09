import ast
import unittest
from isodate.isodates import date
from isodate.duration import Duration

from src.xpyth_parser.conversion.functions.aggregate import Count, Avg, Max, Min, Sum
from src.xpyth_parser.conversion.qname import QName
from src.xpyth_parser.parse import Parser


class FunctionsOperatorsSequences(unittest.TestCase):
    """
    Functions and operators on sequences
    https://www.w3.org/TR/xpath-functions/#sequence-functions
    """

    def test_aggregate_functions(self):

        # Parse a string using Pyparsing
        count = Parser("count(1,2,3)", parseAll=True, no_resolve=True).XPath.expr

        # This returns a Python function which can be used elsewhere
        # The function contains the QName which identifies the function, as well as the arguments

        self.assertTrue(isinstance(count, Count))
        self.assertEqual(count.qname, QName(prefix="fn", localname="count"))
        self.assertEqual(count.arguments[0].value, 1)
        self.assertEqual(count.arguments[1].value, 2)
        self.assertEqual(count.arguments[2].value, 3)

        # Functions can have a run() function which returns a value as described in the Xpath functions document
        #  (e.g., https://www.w3.org/TR/xpath-functions/#func-count)
        self.assertEqual(count.run(), 3)

        avg = Parser("avg(1,4,2,3,12,3,6)", parseAll=True, no_resolve=True).XPath.expr

        self.assertTrue(isinstance(avg, Avg))
        self.assertEqual(avg.qname, QName(prefix="fn", localname="avg"))
        self.assertEqual(avg.arguments[0].value, 1)
        self.assertEqual(avg.arguments[1].value, 4)
        self.assertEqual(avg.arguments[2].value, 2)
        self.assertEqual(avg.arguments[3].value, 3)
        self.assertEqual(avg.arguments[4].value, 12)
        self.assertEqual(avg.arguments[5].value, 3)
        self.assertEqual(avg.arguments[6].value, 6)
        self.assertEqual(avg.run(), 4.428571428571429)

        max = Parser("max(1,4,2,3,12,3,6)", parseAll=True, no_resolve=True).XPath.expr
        self.assertTrue(isinstance(max, Max))
        self.assertEqual(max.qname, QName(prefix="fn", localname="max"))
        self.assertEqual(max.arguments[0].value, 1)
        self.assertEqual(max.arguments[1].value, 4)
        self.assertEqual(max.arguments[2].value, 2)
        self.assertEqual(max.arguments[3].value, 3)
        self.assertEqual(max.arguments[4].value, 12)
        self.assertEqual(max.arguments[5].value, 3)
        self.assertEqual(max.arguments[6].value, 6)
        self.assertEqual(max.run(), 12)

        min = Parser("min(4,2,3,12,3,6)", parseAll=True, no_resolve=True).XPath.expr
        self.assertEqual(min.qname, QName(prefix="fn", localname="min"))
        self.assertTrue(isinstance(min, Min))
        self.assertEqual(min.arguments[0].value, 4)
        self.assertEqual(min.arguments[1].value, 2)
        self.assertEqual(min.arguments[2].value, 3)
        self.assertEqual(min.arguments[3].value, 12)
        self.assertEqual(min.arguments[4].value, 3)
        self.assertEqual(min.arguments[5].value, 6)
        self.assertEqual(min.run(), 2)

        sum = Parser("sum(1,4,2,3,12,3,6)", parseAll=True, no_resolve=True).XPath.expr
        self.assertEqual(sum.qname, QName(prefix="fn", localname="sum"))
        self.assertTrue(isinstance(sum, Sum))
        self.assertEqual(sum.arguments[0].value, 1)
        self.assertEqual(sum.arguments[1].value, 4)
        self.assertEqual(sum.arguments[2].value, 2)
        self.assertEqual(sum.arguments[3].value, 3)
        self.assertEqual(sum.arguments[4].value, 12)
        self.assertEqual(sum.arguments[5].value, 3)
        self.assertEqual(sum.arguments[6].value, 6)
        self.assertEqual(sum.run(), 31)

    def test_date_time(self):

        date_outcome = Parser("xs:date('2021-12-31')")

        self.assertTrue(isinstance(date_outcome.XPath.expr, ast.Constant))
        self.assertTrue(isinstance(date_outcome.XPath.expr.value, date))
        self.assertEqual(date_outcome.XPath.expr.value.day, 31)
        self.assertEqual(date_outcome.XPath.expr.value.month, 12)
        self.assertEqual(date_outcome.XPath.expr.value.year, 2021)

        # Get the date object without having to go through the tree
        date_obj = date_outcome.get_outcome()
        self.assertTrue(isinstance(date_obj, date))
        self.assertEqual(date_obj.day, 31)
        self.assertEqual(date_obj.month, 12)
        self.assertEqual(date_obj.year, 2021)

    def test_year_month_duration(self):
        duration_outcome = Parser("xs:yearMonthDuration('P20Y30M')")

        self.assertTrue(isinstance(duration_outcome.XPath.expr, ast.Constant))
        self.assertTrue(isinstance(duration_outcome.XPath.expr.value, Duration))
        self.assertEqual(duration_outcome.XPath.expr.value.months, 30)
        self.assertEqual(duration_outcome.XPath.expr.value.years, 20)

        # Get the date object without having to go through the tree
        daration_obj = duration_outcome.get_outcome()
        self.assertTrue(isinstance(daration_obj, Duration))
        self.assertEqual(daration_obj.months, 30)
        self.assertEqual(daration_obj.years, 20)

        duration_outcome_2 = Parser("xs:yearMonthDuration('-P1347M')")

        self.assertTrue(isinstance(duration_outcome_2.XPath.expr, ast.Constant))
        self.assertTrue(isinstance(duration_outcome_2.XPath.expr.value, Duration))
        self.assertEqual(duration_outcome_2.XPath.expr.value.months, -1347)

        # Get the date object without having to go through the tree
        daration_obj = duration_outcome_2.get_outcome()
        self.assertTrue(isinstance(daration_obj, Duration))
        self.assertEqual(daration_obj.months, -1347)
