from BaseClasses import LocationProgressType

from . import RE2TestBase
from ..locations import EASTER_EGG_LOCATIONS


class TestLocationSetup(RE2TestBase):
    def test_easter_eggs_are_excluded(self):
        for location_name in EASTER_EGG_LOCATIONS:
            with self.subTest(location=location_name):
                location = self.multiworld.get_location(location_name, self.player)
                self.assertEqual(location.progress_type, LocationProgressType.EXCLUDED)