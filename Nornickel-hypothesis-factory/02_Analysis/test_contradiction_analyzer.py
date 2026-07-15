import unittest

from hypothesis_factory.analysis.contradiction_analyzer import compare_conditions, find_contradictions
from hypothesis_factory.storage import load_demo_claims


class ContradictionAnalyzerTest(unittest.TestCase):
    def test_find_contradictions(self):
        contradictions = find_contradictions(load_demo_claims())
        self.assertTrue(any(zone.type == "contradiction" for zone in contradictions))

    def test_compare_conditions(self):
        claims = load_demo_claims()
        diff = compare_conditions(claims[0], claims[1])
        self.assertIn("condition_a", diff)
        self.assertIn("possible_drivers", diff)


if __name__ == "__main__":
    unittest.main()

