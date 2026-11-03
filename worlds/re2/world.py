from worlds.AutoWorld import World

from . import items, locations, regions, web_world
from . import options as re2_options


class RE2World(World):
    """
    Resident Evil 2 (PS1). Leon and Claire fight their way out of Raccoon City.
    """

    game              = "Resident Evil 2"
    web               = web_world.RE2WebWorld()
    options_dataclass = re2_options.RE2Options
    options: re2_options.RE2Options

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id     = items.ITEM_NAME_TO_ID
    origin_region_name  = "Leon A"

    def create_regions(self) -> None:
        regions.create_all_regions(self)
        locations.create_all_locations(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def create_item(self, name: str) -> items.RE2Item:
        return items.create_item(self, name)

    def get_filler_item_name(self) -> str:
        return items.FILLER_ITEM_NAME

    def set_rules(self) -> None:
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)