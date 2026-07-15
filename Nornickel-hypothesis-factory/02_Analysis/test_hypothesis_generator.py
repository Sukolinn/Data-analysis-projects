import unittest

from hypothesis_factory.pipeline import run_pipeline


class HypothesisGeneratorTest(unittest.TestCase):
    def test_hypotheses_have_origin_zone_and_evidence(self):
        result = run_pipeline("снизить потери элемента 28 / элемента 29 в хвостах")
        self.assertGreaterEqual(len(result.hypotheses), 5)
        for hypothesis in result.hypotheses:
            self.assertTrue(hypothesis.origin_uncertainty_zone.get("id"))
            self.assertTrue(
                hypothesis.evidence
                or hypothesis.knowledge_gaps
                or hypothesis.contradictions
                or hypothesis.indirect_links
            )


if __name__ == "__main__":
    unittest.main()
