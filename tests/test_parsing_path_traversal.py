import unittest
import os
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
        self.assertEqual(
            list(t_PredicateList.parseString("[1]", parseAll=True))[0].val.expr, 1
        )

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
        TESTDATA_FILENAME = os.path.join(
            os.path.dirname(__file__), "input/instance.xml"
        )

        with open(TESTDATA_FILENAME) as xml_file:
            xml_bytes = bytes(xml_file.read(), encoding="utf-8")

            self.assertEqual(
                Parser("count(//singleOccuringElement)", xml=xml_bytes).run(), 1
            )
            self.assertEqual(
                Parser(
                    "count(//singleOccuringElement, $p_val)",
                    xml=xml_bytes,
                    variable_map={"p_val": 300},
                ).run(),
                2,
            )

            # todo: somehow these Exceptions are not raised in test, but they are when tested separately.
            # Throw exception if parameter is not found
            # with self.assertRaises(Exception, Parser, xpath_expr="count(//singleOccuringElement, $p_val)", xml=xml_bytes) as e:
            #
            #     assert e.__str__() == "Variable not in registry: 'p_val'"
            #
            # with self.assertRaises(Exception, Parser, xpath_expr="count(//singleOccuringElement, $p_val)",
            #         xml=xml_bytes,
            #         variable_map={"p_val_fault": 300}):
            #
            #     assert e.__str__() == "Variable not in registry: 'p_val'"

            self.assertEqual(
                Parser("sum(//singleOccuringElement)", xml=xml_bytes).run(), 40000
            )
            self.assertEqual(
                Parser("avg(//singleOccuringElement)", xml=xml_bytes).run(), 40000
            )
            self.assertEqual(
                Parser("min(//singleOccuringElement)", xml=xml_bytes).run(), 40000
            )
            self.assertEqual(
                Parser("max(//singleOccuringElement)", xml=xml_bytes).run(), 40000
            )
            self.assertTrue(
                Parser("count(//singleOccuringElement) eq 1", xml=xml_bytes).run()
            )

            self.assertEqual(
                Parser("count(//doubleOccuringElement)", xml=xml_bytes).run(), 2
            )
            self.assertEqual(
                Parser("sum(//doubleOccuringElement)", xml=xml_bytes).run(), 65000
            )
            self.assertEqual(
                Parser("avg(//doubleOccuringElement)", xml=xml_bytes).run(), 32500
            )
            self.assertEqual(
                Parser("min(//doubleOccuringElement)", xml=xml_bytes).run(), 21000
            )
            self.assertEqual(
                Parser("max(//doubleOccuringElement)", xml=xml_bytes).run(), 44000
            )
            self.assertTrue(
                Parser("count(//doubleOccuringElement) eq 2", xml=xml_bytes).run()
            )

            self.assertEqual(
                Parser("count(//multipleOccuringElement)", xml=xml_bytes).run(), 4
            )
            self.assertEqual(
                Parser("sum(//multipleOccuringElement)", xml=xml_bytes).run(), 72500
            )
            self.assertEqual(
                Parser("avg(//multipleOccuringElement)", xml=xml_bytes).run(), 18125
            )
            self.assertEqual(
                Parser("min(//multipleOccuringElement)", xml=xml_bytes).run(), 1400
            )
            self.assertEqual(
                Parser("max(//multipleOccuringElement)", xml=xml_bytes).run(), 44000
            )
            self.assertTrue(
                Parser("count(//multipleOccuringElement) eq 4", xml=xml_bytes).run()
            )

    def test_predicate_paths(self):
        TESTDATA_FILENAME = os.path.join(
            os.path.dirname(__file__), "input/instance.xml"
        )

        with open(TESTDATA_FILENAME) as xml_file:
            xml_bytes = bytes(xml_file.read(), encoding="utf-8")
            """
            These queries yield LXML elements
            """

            multiple1 = Parser("//multipleOccuringElement[1]", xml=xml_bytes).run(),

            self.assertEqual(multiple1[0][0].text, "44000")
            self.assertEqual(multiple1[0][1].text, "1400")

            multiple2 = Parser("//multipleOccuringElement[2]", xml=xml_bytes).run()
            self.assertEqual(multiple2[0].text, "21000")
            self.assertEqual(multiple2[1].text, "6100")

            multiple3 = Parser(
                    "/maindoc/nested/multipleOccuringElement[2]", xml=xml_bytes
                ).run()
            self.assertEqual(multiple3.text, "21000")

            multiple4 = Parser(
                    "/maindoc/nested/multipleOccuringElement[1]", xml=xml_bytes
                ).run()
            self.assertEqual(multiple4.text, "44000",
            )

            self.assertEqual(
                Parser("/maindoc/doubleOccuringElement[1]", xml=xml_bytes).run().text,
                "44000",
            )

            self.assertEqual(
                Parser("/maindoc/multipleOccuringElement[2]", xml=xml_bytes).run().text,
                "6100",
            )

            self.assertEqual(
                Parser(
                    "/maindoc/doubleNested[2]/multipleDoubleOccuringElement[1]",
                    xml=xml_bytes,
                ).run().text,
                "24527",
            )
            # todo: need to figure out while some queries are in lists, others are not.
            #  I think I am unpacking a bit too much somewhere
