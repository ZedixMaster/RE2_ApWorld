from BaseClasses import CollectionState
from test.bases import WorldTestBase


class RE2TestBase(WorldTestBase):
    game = "Resident Evil 2"

    def locations_in(self, *region_names: str) -> list[str]:
        return [location.name
                for region_name in region_names
                for location in self.multiworld.get_region(region_name, self.player).locations]

    def state_without(self, *item_names: str) -> CollectionState:
        state = CollectionState(self.multiworld)
        for item in self.multiworld.itempool:
            if item.name not in item_names:
                state.collect(item)

        return state