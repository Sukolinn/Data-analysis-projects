import unittest

from hypothesis_factory.analysis.uncertainty_mapper import build_uncertainty_map
from hypothesis_factory.models import UncertaintyZone


class UncertaintyMapperTest(unittest.TestCase):
    def test_build_uncertainty_map_scores_and_sorts(self):
        low = UncertaintyZone(id="A", type="coverage_gap", description="", target_kpi="", kpi_relevance=0.1)
        high = UncertaintyZone(id="B", type="contradiction", description="", target_kpi="", kpi_relevance=1, contradiction_strength=1)
        zones = build_uncertainty_map([low], [high], [])
        self.assertEqual(zones[0].id, "B")
        self.assertGreater(zones[0].priority, 0)


if __name__ == "__main__":
    unittest.main()

