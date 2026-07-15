import unittest

from hypothesis_factory.analysis.indirect_link_analyzer import find_indirect_links
from hypothesis_factory.graph.graph_builder import build_knowledge_graph
from hypothesis_factory.models import EvidenceClaim


class IndirectLinkAnalyzerTest(unittest.TestCase):
    def test_find_indirect_links(self):
        claims = [
            EvidenceClaim(
                id="C1",
                subject="ТОФ element_28 -10",
                relation="concentrated_in",
                object="тонкий класс -10",
                direction="affects",
            ),
            EvidenceClaim(
                id="C2",
                subject="тонкий класс -10",
                relation="points_to",
                object="priority intervention zone",
                direction="affects",
            ),
        ]
        graph = build_knowledge_graph(claims)
        zones = find_indirect_links(graph, "priority intervention zone")
        self.assertTrue(zones)
        self.assertEqual(zones[0].type, "indirect_link")


if __name__ == "__main__":
    unittest.main()
