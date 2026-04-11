import unittest
from configparser import ConfigParser

from lxdrcot.cot_emit import build_status_cot
from lxdrcot.cot_ingest import (
    build_bridge_rx_worker,
    build_error_status_cot,
    classify_payload,
    extract_source_uid,
)
from lxdrcot.cot_map import CasevacRequest, MaintenanceRequest, MappingResult, SupplyRequest
from lxdrcot.router_bridge import accept_mapping


def _event(event_type: str, uid: str, attrs: str = "") -> bytes:
    return (
        f'<event version="2.0" type="{event_type}" uid="{uid}" how="m-g">'
        f"<detail><lxdrcot {attrs} /></detail></event>"
    ).encode()


class TestRouterBridge(unittest.TestCase):
    @staticmethod
    def _fake_pytak():
        class FakeQueueWorker:
            def __init__(self, queue, config) -> None:
                self.queue = queue
                self.config = config

            async def put_queue(self, data, queue_arg=None) -> None:
                target = queue_arg or self.queue
                await target.put(data)

        class FakePyTAK:
            QueueWorker = FakeQueueWorker

        return FakePyTAK

    @staticmethod
    def _config_section():
        config = ConfigParser()
        config["lxdrcot"] = {}
        return config["lxdrcot"]

    @classmethod
    def _run_worker_payload(cls, payload: bytes) -> bytes:
        import asyncio

        async def exercise() -> bytes:
            rx_queue = asyncio.Queue()
            tx_queue = asyncio.Queue()
            worker = build_bridge_rx_worker(
                cls._fake_pytak(),
                rx_queue,
                tx_queue,
                cls._config_section(),
            )
            await worker.handle_data(payload)
            return await tx_queue.get()

        return asyncio.run(exercise())

    def test_bridge_rx_worker_emits_status_event(self) -> None:
        event = self._run_worker_payload(
            _event(
                "b-m-p-s-p-lxdr-maintenance",
                "worker-unit",
                'request_priority="03" maintenance_support="R3" '
                'equipment_nomenclature="FMTV" issue_text="battery dead"',
            )
        )

        self.assertIn(b"lxdrcot-worker-unit-accepted", event)
        self.assertIn(b'detail="maintenance:worker-unit:03:R3:FMTV"', event)

    def test_bridge_rx_worker_emits_invalid_status_event(self) -> None:
        event = self._run_worker_payload(
            _event(
                "b-m-p-s-p-lxdr-maintenance",
                "worker-unit",
                'request_priority="03" maintenance_support="R3" '
                'equipment_nomenclature="FMTV"',
            )
        )

        self.assertIn(b"lxdrcot-worker-unit-invalid", event)
        self.assertIn(b'status="invalid"', event)
        self.assertIn(b'detail="missing maintenance issue_text"', event)

    def test_bridge_rx_worker_emits_supply_status_event(self) -> None:
        event = self._run_worker_payload(
            _event(
                "b-m-p-s-p-lxdr-supply",
                "supply-unit",
                'request_priority="04" item_nomenclature="water" quantity="12" '
                'needed_by="2026-04-11T18:00:00Z"',
            )
        )

        self.assertIn(b"lxdrcot-supply-unit-accepted", event)
        self.assertIn(
            b'detail="supply:supply-unit:04:water:12:2026-04-11T18:00:00Z"',
            event,
        )

    def test_bridge_rx_worker_emits_casevac_status_event(self) -> None:
        event = self._run_worker_payload(
            _event(
                "b-m-p-s-p-lxdr-casevac",
                "casevac-unit",
                'request_priority="01" pickup_location="18S UJ 22850 07080" '
                'patient_count="2" special_equipment="hoist"',
            )
        )

        self.assertIn(b"lxdrcot-casevac-unit-accepted", event)
        self.assertIn(
            b'detail="casevac:casevac-unit:01:18S UJ 22850 07080:2:hoist"',
            event,
        )

    def test_accept_mapping_returns_bridge_outcome(self) -> None:
        m = MappingResult(
            bridge_mode="maintenance",
            source_uid="test-uid",
            raw_payload=b"<event />",
            normalized_request=MaintenanceRequest(
                source_uid="test-uid",
                request_priority="02",
                maintenance_support="R2",
                equipment_nomenclature="JLTV",
                issue_text="starter failed",
            ),
        )

        outcome = accept_mapping(m)

        self.assertTrue(outcome.accepted)
        self.assertEqual(outcome.status_event.status, "accepted")
        self.assertEqual(
            outcome.status_event.detail,
            "maintenance:test-uid:02:R2:JLTV",
        )

    def test_build_status_cot_contains_bridge_fields(self) -> None:
        m = MappingResult(
            bridge_mode="maintenance",
            source_uid="test-uid",
            raw_payload=b"<event />",
            normalized_request=MaintenanceRequest(
                source_uid="test-uid",
                request_priority="02",
                maintenance_support="R2",
                equipment_nomenclature="JLTV",
                issue_text="starter failed",
            ),
        )

        outcome = accept_mapping(m)
        event = build_status_cot(m.source_uid, outcome.status_event)

        self.assertIn(b"lxdrcot-test-uid-accepted", event)
        self.assertIn(b'status="accepted"', event)
        self.assertIn(b'detail="maintenance:test-uid:02:R2:JLTV"', event)

    def test_classify_payload_parses_cot_xml(self) -> None:
        payload = _event(
            "b-m-p-s-p-lxdr-supply",
            "s4-unit-2",
            'request_priority="04" item_nomenclature="battery" quantity="6" '
            'needed_by="2026-04-11T12:00:00Z"',
        )

        m = classify_payload(payload)

        self.assertEqual(m.bridge_mode, "supply")
        self.assertEqual(m.source_uid, "s4-unit-2")
        self.assertEqual(
            m.normalized_request,
            SupplyRequest(
                source_uid="s4-unit-2",
                request_priority="04",
                item_nomenclature="battery",
                quantity="6",
                needed_by="2026-04-11T12:00:00Z",
            ),
        )

    def test_classify_payload_extracts_maintenance_request(self) -> None:
        payload = _event(
            "b-m-p-s-p-lxdr-maintenance",
            "s4-unit-3",
            'request_priority="01" maintenance_support="R1" '
            'equipment_nomenclature="MTVR" issue_text="flat tire"',
        )

        m = classify_payload(payload)

        self.assertEqual(m.bridge_mode, "maintenance")
        self.assertEqual(m.source_uid, "s4-unit-3")
        self.assertIsNotNone(m.normalized_request)

        outcome = accept_mapping(m)

        self.assertEqual(
            outcome.status_event.detail,
            "maintenance:s4-unit-3:01:R1:MTVR",
        )

    def test_classify_payload_extracts_casevac_request(self) -> None:
        payload = _event(
            "b-m-p-s-p-lxdr-casevac",
            "s4-unit-4",
            'request_priority="02" pickup_location="18S UJ 22850 07080" '
            'patient_count="1" special_equipment="none"',
        )

        m = classify_payload(payload)

        self.assertEqual(m.bridge_mode, "casevac")
        self.assertEqual(m.source_uid, "s4-unit-4")
        self.assertEqual(
            m.normalized_request,
            CasevacRequest(
                source_uid="s4-unit-4",
                request_priority="02",
                pickup_location="18S UJ 22850 07080",
                patient_count="1",
                special_equipment="none",
            ),
        )

        outcome = accept_mapping(m)

        self.assertEqual(
            outcome.status_event.detail,
            "casevac:s4-unit-4:02:18S UJ 22850 07080:1:none",
        )

    def test_classify_payload_rejects_invalid_xml(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid CoT XML"):
            classify_payload(b"<event")

    def test_extract_source_uid_falls_back_to_unknown(self) -> None:
        self.assertEqual(extract_source_uid(b"<event"), "unknown")

    def test_build_error_status_cot_uses_source_uid_when_present(self) -> None:
        payload = (
            b'<event version="2.0" type="b-m-p-s-p-lxdr-maintenance" '
            b'uid="bad-unit"></event>'
        )

        event = build_error_status_cot(payload, ValueError("missing CoT detail"))

        self.assertIn(b"lxdrcot-bad-unit-invalid", event)
        self.assertIn(b'status="invalid"', event)
        self.assertIn(b'detail="missing CoT detail"', event)

    def test_accept_mapping_rejects_missing_normalized_maintenance(self) -> None:
        m = MappingResult(
            bridge_mode="maintenance",
            source_uid="test-uid",
            raw_payload=b"<event />",
        )

        with self.assertRaisesRegex(ValueError, "missing normalized maintenance request"):
            accept_mapping(m)

    def test_accept_mapping_returns_supply_bridge_outcome(self) -> None:
        m = MappingResult(
            bridge_mode="supply",
            source_uid="supply-uid",
            raw_payload=b"<event />",
            normalized_request=SupplyRequest(
                source_uid="supply-uid",
                request_priority="05",
                item_nomenclature="fuel",
                quantity="2",
                needed_by="2026-04-12T09:00:00Z",
            ),
        )

        outcome = accept_mapping(m)

        self.assertTrue(outcome.accepted)
        self.assertEqual(
            outcome.status_event.detail,
            "supply:supply-uid:05:fuel:2:2026-04-12T09:00:00Z",
        )

    def test_accept_mapping_returns_casevac_bridge_outcome(self) -> None:
        m = MappingResult(
            bridge_mode="casevac",
            source_uid="casevac-uid",
            raw_payload=b"<event />",
            normalized_request=CasevacRequest(
                source_uid="casevac-uid",
                request_priority="01",
                pickup_location="18S UJ 22850 07080",
                patient_count="3",
                special_equipment="ventilator",
            ),
        )

        outcome = accept_mapping(m)

        self.assertTrue(outcome.accepted)
        self.assertEqual(
            outcome.status_event.detail,
            "casevac:casevac-uid:01:18S UJ 22850 07080:3:ventilator",
        )


if __name__ == "__main__":
    unittest.main()
