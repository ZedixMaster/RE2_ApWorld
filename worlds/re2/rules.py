from __future__ import annotations

from typing import TYPE_CHECKING

from worlds.generic.Rules import set_rule, add_item_rule

AFTER_TURNTABLE_REGIONS = ("Laboratory", "Laboratory B5", "Computer Room", "Active Treatment Room", "Cargo Room", "Gate Platform")

AFTER_TURNTABLE_KEYS = ("Main Fuse", "Fuse Case", "Umbrella Key Card x2", "MO Disk", "Weapon Storage Key")

if TYPE_CHECKING:
    from .world import RE2World

# Puzzle rewards whose pickup only appears once the puzzle is solved, in rooms that are otherwise open.
# Entrance requirements live in regions.CONNECTIONS.
LOCATION_RULES = {
    "Main Hall - Spade Key":         {"Unicorn Medal": 1},
    "Storage Room - King Plug":      {"Red Jewel": 2},
    "Cog Room - Jaguar Stone (R)":   {"Crank": 1, "Cog": 1},  # Knight Plug per both walkthroughs
    "Lounge - Handgun Parts":        {"Small Key": 1},
    "Cold Room - Main Fuse":         {"Fuse Case": 1},
    "P-4 Laboratory - Magnum Parts": {"Weapon Storage Key": 1},
}


def set_all_rules(world: RE2World) -> None:
    for location_name, item_counts in LOCATION_RULES.items():
        set_rule(world.get_location(location_name),
                 lambda state, counts=item_counts: state.has_all_counts(counts, world.player))

    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)

    for region_name in AFTER_TURNTABLE_REGIONS:
        for location in world.get_region(region_name).locations:
            add_item_rule(location, lambda item: allowed_after_turntable(item, world.player))


def allowed_after_turntable(item, player: int) -> bool:
    return item.player != player or not item.advancement or item.name in AFTER_TURNTABLE_KEYS
