import unittest

from src.xpyth_parser.conversion.qname import QName
from src.xpyth_parser.conversion.tests import Test
from src.xpyth_parser.grammar.tests import t_KindTest


class TestKindTests(unittest.TestCase):
    def test_kind_tests(self):
        # Empty document-node
        self.assertEqual(
            list(t_KindTest.parseString(f"document-node()", parseAll=True)),
            [Test(test_type="document-node")],
        )

        # Empty element test
        self.assertEqual(
            list(t_KindTest.parseString(f"element()", parseAll=True)),
            [Test(test_type="element")],
        )

        # document-node with element test
        self.assertEqual(
            list(t_KindTest.parseString(f"document-node(element())", parseAll=True)),
            [Test(test_type="document-node", test=Test(test_type="element"))],
        )

        # document-node with element test and a Qname
        self.assertEqual(
            list(
                t_KindTest.parseString(
                    f"document-node(element(test:element))", parseAll=True
                )
            ),
            [
                Test(
                    test_type="document-node",
                    test=Test(
                        test_type="element",
                        test=QName(prefix="test", localname="element"),
                    ),
                )
            ],
        )

        # document-node with schema element test and a Qname
        self.assertEqual(
            list(
                t_KindTest.parseString(
                    f"document-node(schema-element(element))", parseAll=True
                )
            ),
            [
                Test(
                    test_type="document-node",
                    test=Test(
                        test_type="schema-element", test=QName(localname="element")
                    ),
                )
            ],
        )

        # Empty attribute test
        self.assertEqual(
            list(t_KindTest.parseString(f"attribute()", parseAll=True)), [f"attribute"]
        )

        # Schema-element test
        self.assertEqual(
            list(t_KindTest.parseString(f"schema-element(px:name)", parseAll=True)),
            [
                Test(
                    test_type="schema-element",
                    test=QName(prefix="px", localname="name"),
                )
            ],
        )

        # Schema-element test
        self.assertEqual(
            list(t_KindTest.parseString(f"schema-attribute(px:name)", parseAll=True)),
            [
                Test(
                    test_type="schema-attribute",
                    test=QName(prefix="px", localname="name"),
                )
            ],
        )

        # empty processing-instruction test
        self.assertEqual(
            list(t_KindTest.parseString(f"processing-instruction()", parseAll=True)),
            [Test(test_type="processing-instruction")],
        )

        self.assertEqual(
            list(
                t_KindTest.parseString(f"processing-instruction(name)", parseAll=True)
            ),
            [Test(test_type="processing-instruction", test="name")],
        )

        # empty comment, test and node test
        for keyword in ["comment", "text", "node"]:
            self.assertEqual(
                list(t_KindTest.parseString(f"{keyword}()", parseAll=True)),
                [Test(test_type=f"{keyword}")],
            )
