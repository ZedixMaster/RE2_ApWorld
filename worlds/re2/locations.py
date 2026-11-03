from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Location

from .catalog import LEON_A_LOCATIONS
from .items import RE2Item

if TYPE_CHECKING:
    from .world import RE2World

LOCATION_ID_OFFSET = 1000

LOCATION_NAME_TO_ID = {
    location["name"]: LOCATION_ID_OFFSET + location["flag_index"] for location in LEON_A_LOCATIONS
}


class RE2Location(Location):
    game = "Resident Evil 2"


def create_all_locations(world: RE2World) -> None:
    leon_a = world.get_region("Leon A")
    leon_a.add_locations(LOCATION_NAME_TO_ID, RE2Location)
    leon_a.add_event("Leon A Ending", "Victory", location_type=RE2Location, item_type=RE2Item)