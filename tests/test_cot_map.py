import unittest
from xml.etree.ElementTree import fromstring

from lxdrcot.cot_map import (
    CasevacRequest,
    MaintenanceRequest,
    SupplyRequest,
    classify_event_type,
    is_supported_bridge_mode,
    mapping_from_event,
)


def _event(event_type: str, uid: str, attrs: str = "") -> bytes:
    return (
        f'<event version="2.0" type="{event_type}" uid="{uid}" how="m-g">'
        f"<detail><lxdrcot {attrs} /></detail></event>"
    ).encode()


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
        payload = _event(
            "b-m-p-s-p-lxdr-maintenance",
            "unit-1",
            'request_priority="02" maintenance_support="R2" '
            'equipment_nomenclature="JLTV" issue_text="starter failed"',
        )
        root = fromstring(payload)

        m = mapping_from_event(root, payload)

        self.assertEqual(m.bridge_mode, "maintenance")
        self.assertEqual(m.source_uid, "unit-1")
        self.assertEqual(m.raw_payload, payload)
        self.assertEqual(
            m.normalized_request,
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

    def test_mapping_from_event_extracts_supply_request(self) -> None:
        payload = _event(
            "b-m-p-s-p-lxdr-supply",
            "unit-2",
            'request_priority="03" item_nomenclature="battery" '
            'quantity="4" needed_by="2026-04-11T12:00:00Z"',
        )
        root = fromstring(payload)

        m = mapping_from_event(root, payload)

        self.assertEqual(m.bridge_mode, "supply")
        self.assertEqual(m.source_uid, "unit-2")
        self.assertEqual(
            m.normalized_request,
            SupplyRequest(
                source_uid="unit-2",
                request_priority="03",
                item_nomenclature="battery",
                quantity="4",
                needed_by="2026-04-11T12:00:00Z",
            ),
        )

    def test_mapping_from_event_requires_supply_detail_contract(self) -> None:
        payload = (
            b'<event version="2.0" type="b-m-p-s-p-lxdr-supply" '
            b'uid="unit-2"><detail><lxdrcot request_priority="03" '
            b'item_nomenclature="battery" quantity="4" /></detail></event>'
        )
        root = fromstring(payload)

        with self.assertRaisesRegex(ValueError, "missing supply needed_by"):
            mapping_from_event(root, payload)

    def test_mapping_from_event_extracts_casevac_request(self) -> None:
        payload = _event(
            "b-m-p-s-p-lxdr-casevac",
            "unit-3",
            'request_priority="01" pickup_location="18S UJ 22850 07080" '
            'patient_count="2" special_equipment="hoist"',
        )
        root = fromstring(payload)

        m = mapping_from_event(root, payload)

        self.assertEqual(m.bridge_mode, "casevac")
        self.assertEqual(m.source_uid, "unit-3")
        self.assertEqual(
            m.normalized_request,
            CasevacRequest(
                source_uid="unit-3",
                request_priority="01",
                pickup_location="18S UJ 22850 07080",
                patient_count="2",
                special_equipment="hoist",
            ),
        )

    def test_mapping_from_event_requires_casevac_detail_contract(self) -> None:
        payload = (
            b'<event version="2.0" type="b-m-p-s-p-lxdr-casevac" '
            b'uid="unit-3"><detail><lxdrcot request_priority="01" '
            b'pickup_location="18S UJ 22850 07080" patient_count="2" />'
            b"</detail></event>"
        )
        root = fromstring(payload)

        with self.assertRaisesRegex(ValueError, "missing casevac special_equipment"):
            mapping_from_event(root, payload)


if __name__ == "__main__":
    unittest.main()
