import unittest

from hypothesis_factory.analysis.experiment_planner import suggest_minimal_experiment
from hypothesis_factory.models import UncertaintyZone


class ExperimentPlannerTest(unittest.TestCase):
    def test_each_zone_gets_steps(self):
        for zone_type in ["coverage_gap", "contradiction", "indirect_link", "mechanism_gap", "kpi_gap"]:
            zone = UncertaintyZone(
                id="Z",
                type=zone_type,
                description="",
                target_kpi="",
                linked_entities=["ТОФ", "element_28", "-10"],
                indirect_path=["ТОФ element_28 -10", "тонкий класс -10", "tailings loss"],
            )
            self.assertGreaterEqual(len(suggest_minimal_experiment(zone)), 3)


if __name__ == "__main__":
    unittest.main()
