import unittest

from src.xpyth_parser.conversion.qname import QName
from src.xpyth_parser.conversion.tests import Test
from src.xpyth_parser.grammar.expressions import (
    t_PredicateList,
    t_ForwardAxis,
    t_ForwardStep,
    t_ReverseAxis,
    t_ReverseStep,
)
from src.xpyth_parser.parse import Parser


class PathTraversalTests(unittest.TestCase):
    """
    Test path traversal
    """

    def test_predicates(self):
        """
        Test predicates
        """

        self.assertEqual(list(t_PredicateList.parseString("", parseAll=True)), [])
        self.assertEqual(list(t_PredicateList.parseString("[1]", parseAll=True))[0].expr.value, 1)

    def test_path_expressions(self):
        """
        Test parsing path expressions
        """

        for keyword in [
            "child",
            "descendant",
            "attribute",
            "self",
            "descendant-or-self",
            "following-sibling",
            "following",
            "namespace",
        ]:
            self.assertEqual(
                list(t_ForwardAxis.parseString(f"{keyword}::", parseAll=True)),
                [f"{keyword}", "::"],
            )
            self.assertEqual(
                list(t_ForwardAxis.parseString(f"{keyword} ::", parseAll=True)),
                [f"{keyword}", "::"],
            )

        for keyword in [
            "ancestor",
            "preceding-sibling",
            "preceding",
            "ancestor-or-self",
            "parent",
        ]:
            self.assertEqual(
                list(t_ReverseAxis.parseString(f"{keyword}::", parseAll=True)),
                [f"{keyword}", "::"],
            )
            self.assertEqual(
                list(t_ReverseAxis.parseString(f"{keyword} ::", parseAll=True)),
                [f"{keyword}", "::"],
            )

        # With an element test
        self.assertEqual(
            list(
                t_ForwardStep.parseString(
                    f"following-sibling::element(*)", parseAll=True
                )
            ),
            [f"following-sibling", "::", Test(test_type="element", test="*")],
        )
        self.assertEqual(
            list(
                t_ReverseStep.parseString(
                    f"ancestor-or-self::element(*)", parseAll=True
                )
            ),
            [f"ancestor-or-self", "::", Test(test_type="element", test="*")],
        )

        self.assertEqual(
            list(
                t_ForwardStep.parseString(
                    f"descendant::prefix:localname", parseAll=True
                )
            ),
            [f"descendant", "::", QName(prefix="prefix", localname="localname")],
        )

        self.assertEqual(
            list(
                t_ReverseStep.parseString(
                    f"preceding-sibling::prefix:localname", parseAll=True
                )
            ),
            [f"preceding-sibling", "::", QName(prefix="prefix", localname="localname")],
        )

    def test_path_instance(self):

        with open("input/instance.xml") as xml_file:
            xml_bytes = bytes(xml_file.read(), encoding="utf-8")

            self.assertEqual(Parser("count(//singleOccuringElement)", xml=xml_bytes).run(), 1)
            self.assertEqual(Parser("count(//singleOccuringElement, $p_val)",
                                    xml=xml_bytes, variable_map={"p_val": 300}).run(), 2)

            #Ignore the parameter if no variable_map is given, or the param does not exist in the map
            self.assertEqual(Parser("count(//singleOccuringElement, $p_val)",
                                    xml=xml_bytes).run(), 1)
            self.assertEqual(Parser("count(//singleOccuringElement, $p_val)",
                                    xml=xml_bytes, variable_map={"p_val_fault": 300}).run(), 1)

            self.assertEqual(Parser("sum(//singleOccuringElement)", xml=xml_bytes).run(), 40000)
            self.assertEqual(Parser("avg(//singleOccuringElement)", xml=xml_bytes).run(), 40000)
            self.assertEqual(Parser("min(//singleOccuringElement)", xml=xml_bytes).run(), 40000)
            self.assertEqual(Parser("max(//singleOccuringElement)", xml=xml_bytes).run(), 40000)
            self.assertTrue(Parser("count(//singleOccuringElement) eq 1", xml=xml_bytes).run())


            self.assertEqual(Parser("count(//doubleOccuringElement)", xml=xml_bytes).run(), 2)
            self.assertEqual(Parser("sum(//doubleOccuringElement)", xml=xml_bytes).run(), 65000)
            self.assertEqual(Parser("avg(//doubleOccuringElement)", xml=xml_bytes).run(), 32500)
            self.assertEqual(Parser("min(//doubleOccuringElement)", xml=xml_bytes).run(), 21000)
            self.assertEqual(Parser("max(//doubleOccuringElement)", xml=xml_bytes).run(), 44000)
            self.assertTrue(Parser("count(//doubleOccuringElement) eq 2", xml=xml_bytes).run())

            self.assertEqual(Parser("count(//multipleOccuringElement)", xml=xml_bytes).run(), 4)
            self.assertEqual(Parser("sum(//multipleOccuringElement)", xml=xml_bytes).run(), 72500)
            self.assertEqual(Parser("avg(//multipleOccuringElement)", xml=xml_bytes).run(), 18125)
            self.assertEqual(Parser("min(//multipleOccuringElement)", xml=xml_bytes).run(), 1400)
            self.assertEqual(Parser("max(//multipleOccuringElement)", xml=xml_bytes).run(), 44000)
            self.assertTrue(Parser("count(//multipleOccuringElement) eq 4", xml=xml_bytes).run())

