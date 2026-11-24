from BaseClasses import LocationProgressType

from . import RE2TestBase
from ..locations import EASTER_EGG_LOCATIONS, POINT_OF_NO_RETURN_REGIONS


class TestLocationSetup(RE2TestBase):
    def test_easter_eggs_are_excluded(self):
        for location_name in EASTER_EGG_LOCATIONS:
            with self.subTest(location=location_name):
                location = self.multiworld.get_location(location_name, self.player)
                self.assertEqual(location.progress_type, LocationProgressType.EXCLUDED)

    def test_point_of_no_return_regions_are_excluded(self):
        for location_name in self.locations_in(*POINT_OF_NO_RETURN_REGIONS):
            with self.subTest(location = location_name):
                location = self.multiworld.get_location(location_name, self.player)
                self.assertEqual(location.progress_type, LocationProgressType.EXCLUDED)

    def test_one_club_key_in_pool(self):
        self.assertEqual(len(self.get_items_by_name("Club Key x3")), 1)