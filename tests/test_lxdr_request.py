import unittest

from lxdrcot.cot_map import CasevacRequest, MaintenanceRequest, MappingResult, SupplyRequest
from lxdrcot.lxdr_request import LXDRHeader, LXDRRequestContainer, LXDRSegment, request_from_mapping


class TestLXDRRequest(unittest.TestCase):
    def test_request_from_maintenance_mapping(self) -> None:
        m = MappingResult(
            bridge_mode="maintenance",
            source_uid="maint-1",
            raw_payload=b"<event />",
            normalized_request=MaintenanceRequest(
                source_uid="maint-1",
                request_priority="02",
                maintenance_support="R2",
                equipment_nomenclature="JLTV",
                issue_text="starter failed",
            ),
        )

        req = request_from_mapping(m)

        self.assertEqual(
            req,
            LXDRRequestContainer(
                source_uid="maint-1",
                header=LXDRHeader(
                    local_request_id="maintenance:maint-1",
                    request_priority="02",
                ),
                segment=LXDRSegment(
                    kind="maintenance",
                    fields={
                        "maintenance_support": "R2",
                        "equipment_nomenclature": "JLTV",
                        "issue_text": "starter failed",
                    },
                ),
            ),
        )

    def test_request_from_supply_mapping(self) -> None:
        m = MappingResult(
            bridge_mode="supply",
            source_uid="supply-1",
            raw_payload=b"<event />",
            normalized_request=SupplyRequest(
                source_uid="supply-1",
                request_priority="03",
                item_nomenclature="battery",
                quantity="6",
                needed_by="2026-04-11T12:00:00Z",
            ),
        )

        req = request_from_mapping(m)

        self.assertEqual(req.header.local_request_id, "supply:supply-1")
        self.assertEqual(req.header.request_priority, "03")
        self.assertEqual(req.segment.kind, "supply")
        self.assertEqual(
            req.segment.fields,
            {
                "item_nomenclature": "battery",
                "quantity": "6",
                "needed_by": "2026-04-11T12:00:00Z",
            },
        )

    def test_request_from_casevac_mapping(self) -> None:
        m = MappingResult(
            bridge_mode="casevac",
            source_uid="casevac-1",
            raw_payload=b"<event />",
            normalized_request=CasevacRequest(
                source_uid="casevac-1",
                request_priority="01",
                pickup_location="18S UJ 22850 07080",
                patient_count="2",
                special_equipment="hoist",
            ),
        )

        req = request_from_mapping(m)

        self.assertEqual(req.header.local_request_id, "casevac:casevac-1")
        self.assertEqual(req.segment.kind, "casevac")
        self.assertEqual(
            req.segment.fields,
            {
                "pickup_location": "18S UJ 22850 07080",
                "patient_count": "2",
                "special_equipment": "hoist",
            },
        )

    def test_request_from_mapping_rejects_unknown_mode(self) -> None:
        m = MappingResult(
            bridge_mode="unknown",
            source_uid="unit-1",
            raw_payload=b"<event />",
        )

        with self.assertRaisesRegex(ValueError, "unsupported bridge mode"):
            request_from_mapping(m)
