from __future__ import annotations

from typing import TYPE_CHECKING

from worlds.generic.Rules import set_rule

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
