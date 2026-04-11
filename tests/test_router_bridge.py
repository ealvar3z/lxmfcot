import unittest

from lxdrcot.cot_emit import build_status_cot
from lxdrcot.cot_ingest import classify_payload
from lxdrcot.cot_map import MappingResult
from lxdrcot.router_bridge import accept_mapping


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

        self.assertIn(b"lxdrcot-test-uid-accepted", event)
        self.assertIn(b'status="accepted"', event)
        self.assertIn(b'detail="maintenance:test-uid"', event)

    def test_classify_payload_parses_cot_xml(self) -> None:
        payload = (
            b'<event version="2.0" type="b-m-p-s-p-lxdr-supply" '
            b'uid="s4-unit-2" how="m-g"></event>'
        )

        mapping = classify_payload(payload)

        self.assertEqual(mapping.bridge_mode, "supply")
        self.assertEqual(mapping.source_uid, "s4-unit-2")
        self.assertIsNone(mapping.normalized_request)

    def test_classify_payload_extracts_maintenance_request(self) -> None:
        payload = (
            b'<event version="2.0" type="b-m-p-s-p-lxdr-maintenance" '
            b'uid="s4-unit-3" how="m-g"><detail><lxdrcot request_priority="01" '
            b'maintenance_support="R1" equipment_nomenclature="MTVR" '
            b'issue_text="flat tire" /></detail></event>'
        )

        mapping = classify_payload(payload)

        self.assertEqual(mapping.bridge_mode, "maintenance")
        self.assertEqual(mapping.source_uid, "s4-unit-3")
        self.assertIsNotNone(mapping.normalized_request)

    def test_classify_payload_rejects_invalid_xml(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid CoT XML"):
            classify_payload(b"<event")


if __name__ == "__main__":
    unittest.main()
