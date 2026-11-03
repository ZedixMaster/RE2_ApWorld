from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from .world import RE2World


def create_all_regions(world: RE2World) -> None:
    world.multiworld.regions.append(Region("Leon A", world.player, world.multiworld))