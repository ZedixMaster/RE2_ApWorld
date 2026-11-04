from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Location

from .catalog import LEON_A_LOCATIONS
from .items import RE2Item
from .regions import EVENTS, LOCATION_REGIONS, ROOM_REGIONS

if TYPE_CHECKING:
    from .world import RE2World

LOCATION_ID_OFFSET = 1000

LOCATION_NAME_TO_ID = {
    location["name"]: LOCATION_ID_OFFSET + location["flag_index"] for location in LEON_A_LOCATIONS
}


class RE2Location(Location):
    game = "Resident Evil 2"


def location_region(location: dict) -> str:
    return LOCATION_REGIONS.get(location["name"], ROOM_REGIONS[(location["stage"], location["room"])])


def create_all_locations(world: RE2World) -> None:
    for location in LEON_A_LOCATIONS:
        region = world.get_region(location_region(location))
        region.add_locations({location["name"]: LOCATION_NAME_TO_ID[location["name"]]}, RE2Location)

    for location_name, (region_name, item_name) in EVENTS.items():
        world.get_region(region_name).add_event(location_name, item_name, location_type=RE2Location, item_type=RE2Item)
