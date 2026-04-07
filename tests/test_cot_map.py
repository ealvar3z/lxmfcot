import unittest

from lxmfcot.cot_map import is_supported_bridge_mode


class TestCoTMap(unittest.TestCase):
    def test_supported_bridge_modes(self) -> None:
        self.assertTrue(is_supported_bridge_mode("maintenance"))
        self.assertTrue(is_supported_bridge_mode("supply"))
        self.assertTrue(is_supported_bridge_mode("casevac"))
        self.assertFalse(is_supported_bridge_mode("unknown"))


if __name__ == "__main__":
    unittest.main()
