import unittest

from lxmfcot.cot_map import MappingResult
from lxmfcot.router_bridge import accept_mapping


class TestRouterBridge(unittest.TestCase):
    def test_accept_mapping_returns_bridge_outcome(self) -> None:
        mapping = MappingResult(
            bridge_mode="maintenance",
            source_uid="test-uid",
            raw_payload=b"<event />",
        )

        outcome = accept_mapping(mapping)

        self.assertTrue(outcome.accepted)
        self.assertEqual(outcome.status_event.status, "accepted")
        self.assertEqual(outcome.status_event.detail, "maintenance:test-uid")


if __name__ == "__main__":
    unittest.main()
