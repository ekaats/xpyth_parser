
from isodate import parse_duration, parse_date
from src.xpyth_parser.conversion.functions.generic import Function


class Date(Function):
    """
    Returns a date value
    https://www.w3.org/TR/xpath-functions/#func-dateTime
    https://www.w3.org/TR/xmlschema-2/#date
    """

    def __init__(self, arguments, qname=None):
        super().__init__(arguments, qname, function_name="date")

    def run(self):
        if len(self.arguments) == 0:
            return False
        else:
            date = parse_date(self.arguments[0])
            return date

class YearMonthDuration(Function):
    """
    Returns a date duration value
    https://www.w3.org/TR/xmlschema-2/#duration

    Examples of values:
    P1Y
    P1347Y
    P1347M
    P20Y30M
    -P1347M
    P1Y2M
    """

    def __init__(self, arguments, qname=None):
        super().__init__(arguments, qname, function_name="yearmonthduration")

    def run(self):
        if len(self.arguments) == 0:
            return False
        else:
            duration = parse_duration(self.arguments[0])
            return duration
