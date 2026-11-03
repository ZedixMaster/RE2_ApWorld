from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from .catalog import LEON_A_LOCATIONS

if TYPE_CHECKING:
    from .world import RE2World


# Item Names from BioRand (MIT, Copyright (c) 2022-2026 Ted John): RE2/Re2ItemIds.cs
NATIVE_ITEM_NAMES = {
    0x01: "Knife", 0x02: "Handgun (Leon)", 0x03: "Handgun (Claire)", 0x04: "Custom Handgun",
    0x05: "Magnum", 0x06: "Custom Magnum", 0x07: "Shotgun", 0x08: "Custom Shotgun",
    0x09: "Grenade Launcher (Explosive)", 0x0A: "Grenade Launcher (Flame)", 0x0B: "Grenade Launcher (Acid)",
    0x0C: "Bowgun", 0x0D: "Colt SAA", 0x0E: "Sparkshot", 0x0F: "Sub Machinegun", 0x10: "Flamethrower",
    0x11: "Rocket Launcher", 0x12: "Gatling Gun", 0x13: "Beretta", 0x14: "Handgun Bullets",
    0x15: "Shotgun Shells", 0x16: "Magnum Rounds", 0x17: "Fuel", 0x18: "Grenade Rounds",
    0x19: "Flame Rounds", 0x1A: "Acid Rounds", 0x1B: "Machinegun Bullets", 0x1C: "Sparkshot Battery",
    0x1D: "Bowgun Bolts", 0x1E: "Ink Ribbon", 0x1F: "Small Key", 0x20: "Handgun Parts",
    0x21: "Magnum Parts", 0x22: "Shotgun Parts", 0x23: "First Aid Spray", 0x24: "Antivirus Bomb",
    0x25: "Chemical AC-w", 0x26: "Green Herb", 0x27: "Red Herb", 0x28: "Blue Herb",
    0x29: "Mixed Herb (G+G)", 0x2A: "Mixed Herb (G+R)", 0x2B: "Mixed Herb (G+B)",
    0x2C: "Mixed Herb (G+G+G)", 0x2D: "Mixed Herb (G+G+B)", 0x2E: "Mixed Herb (G+R+B)",
    0x2F: "Lighter", 0x30: "Lockpick", 0x31: "Photo (Sherry)", 0x32: "Valve Handle",
    0x33: "Red Jewel", 0x34: "Red Card Key", 0x35: "Blue Card Key", 0x36: "Serpent Stone",
    0x37: "Jaguar Stone", 0x38: "Jaguar Stone (L)", 0x39: "Jaguar Stone (R)", 0x3A: "Eagle Stone",
    0x3B: "Bishop Plug", 0x3C: "Rook Plug", 0x3D: "Knight Plug", 0x3E: "King Plug",
    0x3F: "Weapon Storage Key", 0x40: "Detonator", 0x41: "C4", 0x42: "C4 + Detonator",
    0x43: "Crank", 0x44: "Film A", 0x45: "Film B", 0x46: "Film C", 0x47: "Unicorn Medal",
    0x48: "Eagle Medal", 0x49: "Wolf Medal", 0x4A: "Cog", 0x4B: "Manhole Opener",
    0x4C: "Main Fuse", 0x4D: "Fuse Case", 0x4E: "Vaccine", 0x4F: "Vaccine Cartridge",
    0x50: "Film D", 0x51: "Vaccine Base", 0x52: "G-Virus", 0x53: "Special Key",
    0x54: "Joint Plug (Blue)", 0x55: "Joint Plug (Red)", 0x56: "Cord", 0x57: "Photo (Ada)",
    0x58: "Cabin Key", 0x59: "Spade Key", 0x5A: "Diamond Key", 0x5B: "Heart Key",
    0x5C: "Club Key", 0x5D: "Down Key", 0x5E: "Up Key", 0x5F: "Power Room Key",
    0x60: "MO Disk", 0x61: "Umbrella Key Card", 0x62: "Master Key", 0x63: "Platform Key",
}

WEAPONS_AND_UPGRADES = set(range(0x01, 0x14)) | {0x1F, 0x20, 0x21, 0x22}
FIRST_KEY_ITEM       = 0x2F
NOT_PROGRESSION      = {0x31, 0x52, 0x57}

FILLER_ITEM_NAME     = "Green Herb"


def item_name(native_id: int, amount: int) -> str:
    name = NATIVE_ITEM_NAMES[native_id]
    return name if amount == 1 else f"{name} x{amount}"


def item_id(native_id: int, amount: int) -> int:
    return native_id * 1000 + amount


VANILLA_ITEMS = [(location["item_id"], location["amount"]) for location in LEON_A_LOCATIONS]

ITEM_NAME_TO_ID = {item_name(*item): item_id(*item) for item in VANILLA_ITEMS}


def classification(native_id: int) -> ItemClassification:
    if native_id >= FIRST_KEY_ITEM and native_id not in NOT_PROGRESSION:
        return ItemClassification.progression
    if native_id in WEAPONS_AND_UPGRADES:
        return ItemClassification.useful
    return ItemClassification.filler


class RE2Item(Item):
    game = "Resident Evil 2"


def create_item(world: RE2World, name: str) -> RE2Item:
    native_id = world.item_name_to_id[name] // 1000
    return RE2Item(name, classification(native_id), world.item_name_to_id[name], world.player)


def create_all_items(world: RE2World) -> None:
    world.multiworld.itempool += [world.create_item(item_name(*item)) for item in VANILLA_ITEMS]