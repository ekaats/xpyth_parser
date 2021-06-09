
import unittest

from conversion.qname import QName
from conversion.tests import Test
from grammar.expressions import t_PredicateList, t_ForwardAxis, t_ForwardStep, t_ReverseAxis, t_ReverseStep

class PathTraversalTests(unittest.TestCase):


    def test_predicates(self):
        self.assertEqual(list(t_PredicateList.parseString("", parseAll=True)), [])
        self.assertEqual(list(t_PredicateList.parseString("[1]", parseAll=True)), ["[", 1, "]"])

    def test_path_expressions(self):
        for keyword in ["child", "descendant", "attribute", "self", "descendant-or-self", "following-sibling", "following", "namespace"]:
            self.assertEqual(list(t_ForwardAxis.parseString(f"{keyword}::", parseAll=True)), [f"{keyword}", "::"])
            self.assertEqual(list(t_ForwardAxis.parseString(f"{keyword} ::", parseAll=True)), [f"{keyword}", "::"])

        for keyword in ["ancestor", "preceding-sibling", "preceding", "ancestor-or-self", "parent"]:
            self.assertEqual(list(t_ReverseAxis.parseString(f"{keyword}::", parseAll=True)), [f"{keyword}", "::"])
            self.assertEqual(list(t_ReverseAxis.parseString(f"{keyword} ::", parseAll=True)), [f"{keyword}", "::"])

        # With an element test
        self.assertEqual(list(t_ForwardStep.parseString(f"following-sibling::element(*)", parseAll=True)),
                         [f"following-sibling", "::", Test(test_type="element", test="*")])
        self.assertEqual(list(t_ReverseStep.parseString(f"ancestor-or-self::element(*)", parseAll=True)),
                         [f"ancestor-or-self", "::", Test(test_type="element", test="*")])

        self.assertEqual(list(t_ForwardStep.parseString(f"descendant::prefix:localname", parseAll=True)),
                         [f"descendant", "::", QName(prefix="prefix", localname='localname')])

        self.assertEqual(list(t_ReverseStep.parseString(f"preceding-sibling::prefix:localname", parseAll=True)),
                         [f"preceding-sibling", "::", QName(prefix="prefix", localname='localname')])

if __name__ == '__main__':
    unittest.main()