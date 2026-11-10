import unittest

from ..catalog import LEON_A_LOCATIONS
from ..client import EMPTY_RECORD, INVENTORY_SLOTS, find_any_vanilla_slot

LAB_SMG = next(location for location in LEON_A_LOCATIONS if location["name"] == "Culture Experiment Room - Sub Machinegun")


def inventory_with(first_slot: bytes) -> bytes:
    return first_slot + EMPTY_RECORD * (INVENTORY_SLOTS - 1)


class TestVanillaRemoval(unittest.TestCase):
    def test_finds_the_sub_machinegun(self):
        before = inventory_with(EMPTY_RECORD)
        after  = inventory_with(bytes([0x0F, 100, 0, 0]))
        self.assertEqual(find_any_vanilla_slot(before, after, LAB_SMG), 0)


    def test_finds_the_bullets_given_instead(self):
        before = inventory_with(EMPTY_RECORD)
        after  = inventory_with(bytes([0x1B, 100, 0, 0]))
        self.assertEqual(find_any_vanilla_slot(before, after, LAB_SMG), 0)


    def test_ignores_an_unrelated_item(self):
        before = inventory_with(EMPTY_RECORD)
        after  = inventory_with(bytes([0x14, 15, 0, 0]))
        self.assertIsNone(find_any_vanilla_slot(before, after, LAB_SMG))