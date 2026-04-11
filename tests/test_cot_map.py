import unittest
from xml.etree.ElementTree import fromstring

from lxdrcot.cot_map import (
    MaintenanceRequest,
    classify_event_type,
    is_supported_bridge_mode,
    mapping_from_event,
)


class TestCoTMap(unittest.TestCase):
    def test_supported_bridge_modes(self) -> None:
        self.assertTrue(is_supported_bridge_mode("maintenance"))
        self.assertTrue(is_supported_bridge_mode("supply"))
        self.assertTrue(is_supported_bridge_mode("casevac"))
        self.assertFalse(is_supported_bridge_mode("unknown"))

    def test_classify_event_type(self) -> None:
        self.assertEqual(
            classify_event_type("b-m-p-s-p-lxdr-maintenance"),
            "maintenance",
        )
        self.assertEqual(
            classify_event_type("b-m-p-s-p-lxdr-supply"),
            "supply",
        )
        self.assertEqual(
            classify_event_type("b-m-p-s-p-lxdr-casevac"),
            "casevac",
        )

    def test_mapping_from_event(self) -> None:
        payload = (
            b'<event version="2.0" type="b-m-p-s-p-lxdr-maintenance" '
            b'uid="unit-1" how="m-g"><detail><lxdrcot request_priority="02" '
            b'maintenance_support="R2" equipment_nomenclature="JLTV" '
            b'issue_text="starter failed" /></detail></event>'
        )
        root = fromstring(payload)

        mapping = mapping_from_event(root, payload)

        self.assertEqual(mapping.bridge_mode, "maintenance")
        self.assertEqual(mapping.source_uid, "unit-1")
        self.assertEqual(mapping.raw_payload, payload)
        self.assertEqual(
            mapping.normalized_request,
            MaintenanceRequest(
                source_uid="unit-1",
                request_priority="02",
                maintenance_support="R2",
                equipment_nomenclature="JLTV",
                issue_text="starter failed",
            ),
        )

    def test_mapping_from_event_requires_uid(self) -> None:
        payload = (
            b'<event version="2.0" type="b-m-p-s-p-lxdr-maintenance">'
            b'<detail><lxdrcot request_priority="02" maintenance_support="R2" '
            b'equipment_nomenclature="JLTV" issue_text="starter failed" /></detail>'
            b"</event>"
        )
        root = fromstring(payload)

        with self.assertRaisesRegex(ValueError, "missing CoT uid"):
            mapping_from_event(root, payload)

    def test_mapping_from_event_rejects_unknown_type(self) -> None:
        payload = b'<event version="2.0" type="a-f-G-U-C" uid="unit-1"></event>'
        root = fromstring(payload)

        with self.assertRaisesRegex(ValueError, "unsupported CoT event type"):
            mapping_from_event(root, payload)

    def test_mapping_from_event_requires_maintenance_detail_contract(self) -> None:
        payload = (
            b'<event version="2.0" type="b-m-p-s-p-lxdr-maintenance" '
            b'uid="unit-1"><detail><lxdrcot request_priority="02" '
            b'maintenance_support="R2" equipment_nomenclature="JLTV" />'
            b"</detail></event>"
        )
        root = fromstring(payload)

        with self.assertRaisesRegex(ValueError, "missing maintenance issue_text"):
            mapping_from_event(root, payload)


if __name__ == "__main__":
    unittest.main()
