import unittest

from hypothesis_factory.analysis.coverage_analyzer import build_coverage_matrix, find_coverage_gaps
from hypothesis_factory.extraction.entity_extractor import extract_entities
from hypothesis_factory.storage import load_demo_claims, load_demo_documents


class GapAnalyzerTest(unittest.TestCase):
    def test_find_coverage_gaps(self):
        docs = load_demo_documents()
        claims = load_demo_claims()
        entities = extract_entities(docs, claims)
        matrix = build_coverage_matrix(claims, entities, "снизить потери элемента 28 / элемента 29 в хвостах")
        gaps = find_coverage_gaps(matrix, "снизить потери элемента 28 / элемента 29 в хвостах")
        self.assertTrue(gaps)
        self.assertTrue(all(zone.type == "coverage_gap" for zone in gaps))


if __name__ == "__main__":
    unittest.main()
