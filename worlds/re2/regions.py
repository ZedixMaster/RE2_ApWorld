from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from .world import RE2World

# Leon A regions, split at every lock in tools/research/leon_a_locks.md. Each key door gets its own region so a
# key door shuffle can later change the entrance rules without moving rooms.
# Keyed by (stage byte, room byte). Rooms Leon A never enters are left out (see UNREACHABLE_ROOMS in build_catalog.py).
ROOM_REGIONS = {
    # City, before the point of no return at the R.P.D. gate
    (0, 0x00): "City", (0, 0x01): "City", (0, 0x02): "City", (0, 0x18): "City",
    (0, 0x19): "City", (0, 0x1A): "City", (0, 0x1B): "City", (0, 0x03): "City",

    # Entry: Marvin gives the Blue Card Key in the West Office, then that door locks behind Leon
    (1, 0x00): "Main Hall",

    # Blue Card Key (Main Hall computer)
    (1, 0x01): "RPD West Wing", (1, 0x04): "RPD West Wing", (1, 0x05): "RPD West Wing",
    (1, 0x06): "RPD West Wing", (1, 0x07): "RPD West Wing", (1, 0x08): "RPD West Wing",
    (0, 0x0C): "RPD West Wing", (0, 0x14): "RPD West Wing", (0, 0x15): "RPD West Wing",

    (1, 0x0A): "RPD East Wing", (1, 0x0B): "RPD East Wing", (1, 0x0C): "RPD East Wing",
    (0, 0x16): "RPD East Wing",

    # Spade Key
    (1, 0x03): "File Storage",
    (0, 0x13): "RPD 2F", (0, 0x12): "RPD 2F", (0, 0x10): "RPD 2F", (0, 0x17): "RPD 2F",
    (0, 0x0F): "RPD 2F", (0, 0x11): "RPD 2F", (0, 0x0A): "RPD 2F",
    (0, 0x09): "Rooftop", (0, 0x08): "Rooftop", (0, 0x07): "Rooftop", (0, 0x06): "Rooftop",

    # Valve Handle (helicopter fire)
    (0, 0x0B): "Storage Room",

    # Diamond Key; the West Office opens again from the Evidence Room side
    (1, 0x09): "Evidence Room",
    (1, 0x02): "West Office",
    (1, 0x0E): "Interrogation Room",

    # Heart Key
    (1, 0x0F): "RPD Basement", (1, 0x11): "RPD Basement", (1, 0x12): "RPD Basement",
    (1, 0x13): "RPD Basement", (1, 0x16): "RPD Basement", (1, 0x19): "RPD Basement",
    (1, 0x1A): "RPD Basement", (2, 0x01): "RPD Basement",

    # Club Key, Red Card Key
    (1, 0x0D): "Press Room",
    (1, 0x10): "Watchman's Room",
    (1, 0x15): "Autopsy Room",
    (1, 0x14): "Arms Storage",

    # Manhole Opener (Kennel)
    (2, 0x02): "Sewage Disposal", (2, 0x0B): "Sewage Disposal", (2, 0x03): "Sewage Disposal",
    (2, 0x0C): "Sewage Disposal",

    # Ada's first section
    (2, 0x05): "Ada Sewage Disposal", (2, 0x06): "Ada Sewage Disposal", (2, 0x07): "Ada Sewage Disposal",
    (2, 0x0D): "Ada Sewage Disposal",

    # Bishop, Rook, King and Knight Plugs (Septic Pool Walkway panel)
    (2, 0x04): "Sewers", (3, 0x02): "Sewers", (3, 0x03): "Sewers", (3, 0x04): "Sewers",
    (3, 0x05): "Sewers", (3, 0x07): "Sewers", (3, 0x0B): "Sewers",

    # Valve Handle (Water Pool bridge)
    (3, 0x08): "Sewers Water Pool Side", (3, 0x0A): "Sewers Water Pool Side",
    (3, 0x10): "Sewers Water Pool Side", (3, 0x09): "Sewers Water Pool Side",

    # Eagle and Wolf Medals (waterfall); the tram back to the sewers is two-way
    (3, 0x0D): "Factory", (3, 0x0E): "Factory", (4, 0x00): "Factory", (4, 0x01): "Factory",
    (4, 0x02): "Factory", (4, 0x08): "Factory", (4, 0x03): "Factory", (4, 0x04): "Factory",
    (4, 0x05): "Factory",

    # Down Key: turntable descent, point of no return
    (4, 0x09): "Laboratory", (5, 0x00): "Laboratory", (5, 0x01): "Laboratory", (5, 0x02): "Laboratory",
    (5, 0x03): "Laboratory", (5, 0x05): "Laboratory", (5, 0x06): "Laboratory", (5, 0x07): "Laboratory",
    (5, 0x08): "Laboratory", (5, 0x11): "Laboratory", (5, 0x0B): "Laboratory", (5, 0x0C): "Laboratory",
    (5, 0x0D): "Laboratory", (5, 0x0F): "Laboratory", (5, 0x09): "Laboratory", (5, 0x0A): "Laboratory",

    # Main Fuse (lab power opens the West Area shutter)
    (5, 0x0E): "Laboratory B5", (5, 0x16): "Laboratory B5", (5, 0x12): "Laboratory B5",
    (5, 0x14): "Laboratory B5", (5, 0x15): "Laboratory B5",

    # Umbrella Key Card
    (5, 0x13): "Computer Room",
    (5, 0x10): "Active Treatment Room",

    # MO Disk, then the elevator down to the ending
    (5, 0x17): "Cargo Room",
    (6, 0x00): "Gate Platform",
}

# (from region, to region, items needed). Only the direction Leon first walks through matters for logic.
CONNECTIONS = [
    ("City",                "Main Hall",              ()),  # point of no return
    ("Main Hall",           "RPD West Wing",          ("Blue Card Key",)),
    ("Main Hall",           "RPD East Wing",          ("Blue Card Key",)),
    ("RPD West Wing",       "File Storage",           ("Spade Key x2",)),
    ("RPD West Wing",       "RPD 2F",                 ("Spade Key x2",)),
    ("RPD 2F",              "Rooftop",                ()),
    ("RPD 2F",              "Storage Room",           ("Valve Handle",)),
    ("RPD West Wing",       "Evidence Room",          ("Diamond Key x2",)),
    ("Evidence Room",       "West Office",            ()),
    ("RPD East Wing",       "Interrogation Room",     ("Diamond Key x2",)),
    ("RPD East Wing",       "Press Room",             ("Club Key x3",)),
    ("RPD East Wing",       "RPD Basement",           ("Heart Key",)),
    ("RPD Basement",        "Watchman's Room",        ("Club Key x3",)),
    ("RPD Basement",        "Autopsy Room",           ("Club Key x3",)),
    ("RPD Basement",        "Arms Storage",           ("Red Card Key",)),
    ("RPD Basement",        "Sewage Disposal",        ("Manhole Opener",)),
    ("Sewage Disposal",     "Ada Sewage Disposal",    ()),
    # The Cog Room item reads 0x39 on the disc; both walkthroughs call it the Knight Plug. Rename after the in-game test.
    ("Sewage Disposal",     "Sewers",                 ("Bishop Plug", "Rook Plug", "King Plug", "Jaguar Stone (R)")),
    ("Sewers",              "Sewers Water Pool Side", ("Valve Handle",)),
    ("Sewers",              "Factory",                ("Eagle Medal", "Wolf Medal")),
    ("Factory",             "Laboratory",             ("Down Key",)),  # point of no return
    ("Laboratory",          "Laboratory B5",          ("Main Fuse",)),
    ("Laboratory B5",       "Computer Room",          ("Umbrella Key Card x2",)),
    ("Laboratory",          "Active Treatment Room",  ("Umbrella Key Card x2", "Computer Room Login")),
    # The MO Disk shutter is used during the self-destruct, which Annette starts in the Active Treatment Room
    ("Laboratory B5",       "Cargo Room",             ("MO Disk", "Self-Destruct Sequence")),
    ("Cargo Room",          "Gate Platform",          ()),
]

# Story events the logic needs, as event location name: (region, event item).
EVENTS = {
    "Marvin's Blue Card Key":      ("Main Hall",     "Blue Card Key"),
    "Computer Room - GUEST Login": ("Computer Room", "Computer Room Login"),
    "Annette Starts Self-Destruct": ("Active Treatment Room", "Self-Destruct Sequence"),
    "Leon A Ending":               ("Gate Platform", "Victory"),
}

# Locations that belong to a different region than their room.
LOCATION_REGIONS = {
    # Leon's hand-off copies of Ada's pickups only appear after her section
    "Septic Pool Entrance - Club Key":       "Ada Sewage Disposal",
    "Septic Pool Entrance - Shotgun Shells": "Ada Sewage Disposal",
}


def requirement_rule(world: RE2World, items: tuple[str, ...]):
    if not items:
        return None
    return lambda state: state.has_all(items, world.player)


def create_all_regions(world: RE2World) -> None:
    for name in dict.fromkeys(ROOM_REGIONS.values()):
        world.multiworld.regions.append(Region(name, world.player, world.multiworld))

    for source, target, items in CONNECTIONS:
        world.get_region(source).connect(world.get_region(target), f"{source} -> {target}",
                                         requirement_rule(world, items))