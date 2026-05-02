import unittest

from lxdrcot.local_router import LocalLXDRRouter
from lxdrcot.lxdr_request import LXDRHeader, LXDRRequestContainer, LXDRSegment


class TestLocalLXDRRouter(unittest.TestCase):
    def test_submit_tracks_request(self) -> None:
        router = LocalLXDRRouter()
        req = LXDRRequestContainer(
            source_uid="unit-1",
            header=LXDRHeader(
                local_request_id="maintenance:unit-1",
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
        )

        out = router.submit(req)

        self.assertEqual(out, req)
        self.assertEqual(router.submitted_requests(), [req])
