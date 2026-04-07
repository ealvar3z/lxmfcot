import unittest

from lxmfcot.cot_emit import build_status_cot
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

    def test_build_status_cot_contains_bridge_fields(self) -> None:
        mapping = MappingResult(
            bridge_mode="maintenance",
            source_uid="test-uid",
            raw_payload=b"<event />",
        )

        outcome = accept_mapping(mapping)
        event = build_status_cot(mapping.source_uid, outcome.status_event)

        self.assertIn(b"lxmfcot-test-uid-accepted", event)
        self.assertIn(b'status="accepted"', event)
        self.assertIn(b'detail="maintenance:test-uid"', event)


if __name__ == "__main__":
    unittest.main()
