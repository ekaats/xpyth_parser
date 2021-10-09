import unittest
from isodate.isodates import date
from isodate.duration import Duration

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

        self.assertTrue(count.__str__(), "fn_count")
        self.assertEqual(count.args[0], [1,2,3])


        # Functions can have a run() function which returns a value as described in the Xpath functions document
        #  (e.g., https://www.w3.org/TR/xpath-functions/#func-count)
        self.assertEqual(count(), 3)

        avg = Parser("avg(1,4,2,3,12,3,6)", parseAll=True, no_resolve=True).XPath.expr

        self.assertTrue(avg.__str__(), "fn_avg")
        self.assertEqual(avg.args[0], [1,4,2,3,12,3,6])
        self.assertEqual(avg(), 4.428571428571429)

        max = Parser("max(1,4,2,3,12,3,6)", parseAll=True, no_resolve=True).XPath.expr
        self.assertTrue(max.__str__(), "fn_max")
        self.assertEqual(max.args[0], [1, 4, 2, 3, 12, 3, 6])
        self.assertEqual(max(), 12)

        min = Parser("min(4,2,3,12,3,6)", parseAll=True, no_resolve=True).XPath.expr
        self.assertTrue(min.__str__(), "fn_min")
        self.assertEqual(min.args[0], [4, 2, 3, 12, 3, 6])
        self.assertEqual(min(), 2)

        sum = Parser("sum(1,4,2,3,12,3,6)", parseAll=True, no_resolve=True).XPath.expr
        self.assertTrue(sum.__str__(), "fn_sum")
        self.assertEqual(sum.args[0], [1, 4, 2, 3, 12, 3, 6])
        self.assertEqual(sum(), 31)

    def test_date_time(self):

        date_outcome = Parser("xs:date('2021-12-31')")

        self.assertTrue(sum.__str__(), "xs_date")

        # Get the date object without having to go through the tree
        date_obj = date_outcome.resolved_answer
        self.assertTrue(isinstance(date_obj, date))
        self.assertTrue(isinstance(date_obj, date))
        self.assertEqual(date_obj.day, 31)
        self.assertEqual(date_obj.month, 12)
        self.assertEqual(date_obj.year, 2021)

    def test_year_month_duration(self):
        duration_outcome = Parser("xs:yearMonthDuration('P20Y30M')")

        self.assertTrue(duration_outcome.__str__(), "xs_yearMonthDuration")
        self.assertEqual(duration_outcome.XPath.expr.args[0], 'P20Y30M')

        # Get the date object without having to go through the tree
        daration_obj = duration_outcome.resolved_answer
        self.assertTrue(daration_obj.__str__(), "xs_yearMonthDuration")
        self.assertEqual(daration_obj.months, 30)
        self.assertEqual(daration_obj.years, 20)

        duration_outcome_2 = Parser("xs:yearMonthDuration('-P1347M')")

        self.assertTrue(duration_outcome_2.__str__(), "xs_yearMonthDuration")

        # Get the date object without having to go through the tree
        daration_obj = duration_outcome_2.resolved_answer
        self.assertTrue(isinstance(daration_obj, Duration))
        self.assertEqual(daration_obj.months, -1347)

    def test_qname(self):
        self.assertEqual(Parser("xs:QName(\'prefix:localname\')").resolved_answer,
                         QName(localname="localname", prefix="prefix"))
        self.assertEqual(Parser("xs:QName(\'http://example/thing\', \'prefix:localname\')").resolved_answer,
                         QName(localname="localname", prefix="prefix", namespace="http://example/thing"))

    def test_number(self):
        self.assertEqual(Parser("number(42)").resolved_answer, 42.0)
        self.assertEqual(Parser("number(42.42)").resolved_answer, 42.42)
        self.assertEqual(Parser("number($paramname)", variable_map={"paramname": 42.42}).resolved_answer, 42.42)