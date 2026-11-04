import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from room_names import ROOM_NAMES

# Item names from BioRand (MIT, Copyright (c) 2022-2026 Ted John): RE2/Re2ItemIds.cs
ITEM_NAMES = {
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
LAST_ITEM_ID = 0x63

LEON_A_FLAGS = {(1, 0): 0, (1, 1): 0}

FIRST_LATE_STAGE  = 4
LATE_STAGE_OFFSET = 256

# Spots the flags alone can't settle. Value = (item_type, amount, global_id), or None to leave the spot out.
REVIEW_DECISIONS = {
    ("ROOM10D0.RDT", 10): (0x16, 8, 206),
    ("ROOM1150.RDT", 7):  None,
    ("ROOM20C0.RDT", 10): (0x15, 7, 207),
    ("ROOM20D0.RDT", 20): (0x14, 30, 208),
    ("ROOM20E0.RDT", 3):  (0x3C, 1, 56),
    ("ROOM3010.RDT", 3):  None,
    ("ROOM30B0.RDT", 4):  (0x5C, 3, 124),
    ("ROOM30B0.RDT", 5):  (0x15, 7, 193),
    ("ROOM30C0.RDT", 5):  None,
    ("ROOM40E0.RDT", 7):  (0x15, 7, 202),
    ("ROOM40E0.RDT", 8):  (0x14, 15, 203),
    ("ROOM4100.RDT", 6):  (0x23, 1, 180),
    ("ROOM5060.RDT", 2):  None,  # Same pickup as ROOM5040 aot 2: the platform with the turntable down
    ("ROOM5070.RDT", 4):  (0x15, 7, 76),
    ("ROOM60C0.RDT", 7):  None,
    ("ROOM60F0.RDT", 2):  (0x0F, 100, 30),
    ("ROOM7040.RDT", 2):  (0x1E, 3, 78),
    ("ROOM7040.RDT", 3):  (0x63, 1, 79),
}

# Rooms Leon A never enters, keyed by (stage, room). Their item scripts are unconditional, so the flags can't drop them.
# Evidence is in leon_a_locks.md (door graph, Evil Resource, cvxfreak's walkthrough).
UNREACHABLE_ROOMS = {
    (0, 0x05): "R.P.D. Backyard: only reachable from East Street, the B start",
    (0, 0x0D): "Stuffed Tiger Corridor: only reachable through the Chief's office",
    (0, 0x0E): "Taxidermy Display Room: only reachable through the Chief's office",
    (1, 0x1B): "Chief Irons' Office: blocked door in Leon A",
    (3, 0x01): "Control Room 1 / Warehouse 1: the 'T' Corridor door leads here only for Claire",
    (4, 0x06): "Turntable Yard (Turntable Lowered): B only",
    (4, 0x07): "Hydrolic Monitor Room: B only",
    (5, 0x04): "Power Room: needs the Power Room Key, B only",
    (6, 0x01): "Main Platform: needs the Platform Key, B only",
    (6, 0x02): "Power Control Platform: past the Main Platform",
    (6, 0x03): "Train Front Carriage: B ending",
    (6, 0x04): "Train Rear Carriage: B only",
}


def load_rows(csv_path):
    with open(csv_path, newline="") as source:
        return [row for row in csv.DictReader(source) if row["reachable"] == "True"]


def group_spots(rows):
    spots = defaultdict(list)
    for row in rows:
        spots[(row["file"], int(row["aot_id"]))].append(row)

    return spots


def variants(entries):
    return sorted({(int(entry["item_type"], 16), int(entry["amount"]), int(entry["global_id"])) for entry in entries})


def describe(item_type, amount):
    if item_type > LAST_ITEM_ID:
        return f"File 0x{item_type:02X}"
    return f"{ITEM_NAMES.get(item_type, f'Unknown 0x{item_type:02X}')} x{amount}"


def report(spots):
    single   = {key: entries for key, entries in spots.items() if len(variants(entries)) == 1}
    multiple = {key: entries for key, entries in spots.items() if len(variants(entries)) > 1}
    print(f"{len(spots)} spots: {len(single)} with one variant, {len(multiple)} with several")

    for (file, aot_id), entries in sorted(multiple.items()):
        print(f"  {file} aot {aot_id}:")
        for entry in entries:
            item_type = int(entry["item_type"], 16)
            print(f"    {describe(item_type, entry['amount'])} [gid {entry['global_id']}] if {entry['conditions'] or 'always'}")


def check_result(check, known_flags):
    name, *arguments = check
    if name != "ck":
        return None
    bit_array, index, expected = arguments
    actual = known_flags.get((bit_array, index))
    return None if actual is None else actual == expected


def all_of(results):
    if False in results:
        return False
    if None in results:
        return None
    return True


def evaluate(condition_json, known_flags):
    block_results = []
    for block in json.loads(condition_json):
        result = all_of([check_result(check, known_flags) for check in block["checks"]])
        if block["negated"] and result is not None:
            result = not result
        block_results.append(result)
    return all_of(block_results)


def resolve(spots, known_flags):
    included, review, excluded = {}, {}, []
    for key, entries in sorted(spots.items()):
        results = [(evaluate(entry["condition_json"], known_flags), entry) for entry in entries]
        if any(result is None for result, _ in results):
            review[key] = results
        elif any(result for result, _ in results):
            included[key] = variants([entry for result, entry in results if result])
        else:
            excluded.append(key)

    print(f"{len(included)} Leon A spots, {len(excluded)} not in Leon A, {len(review)} need review")
    for (file, aot_id), options in included.items():
        if len(options) > 1:
            print(f"  STILL AMBIGUOUS {file} aot {aot_id}: {options}")
    for (file, aot_id), results in review.items():
        print(f"  REVIEW {file} aot {aot_id}:")
        for result, entry in results:
            print(f"      {result!s:<5} {describe(int(entry['item_type'], 16), entry['amount'])} [gid {entry['global_id']}] if {entry['conditions'] or 'always'}")
    return included, review, excluded


def apply_decisions(included, review):
    unsettled = [key for key, options in included.items() if len(options) > 1] + list(review)
    for file, aot_id in unsettled:
        if (file, aot_id) not in REVIEW_DECISIONS:
            print(f"  NO DECISION {file} aot {aot_id}")

    chosen = {key: options[0] for key, options in included.items() if len(options) == 1}
    for key, decision in REVIEW_DECISIONS.items():
        if decision is None:
            chosen.pop(key, None)
        else:
            chosen[key] = decision

    return {key: variant for key, variant in chosen.items() if variant[0] <= LAST_ITEM_ID}


def stage_and_room(file):
    return int(file[4], 16) - 1, int(file[5:7], 16)


def drop_unreachable(chosen):
    dropped = {key for key in chosen if stage_and_room(key[0]) in UNREACHABLE_ROOMS}
    for file, aot_id in sorted(dropped):
        stage, room = stage_and_room(file)
        print(f"  UNREACHABLE {file} aot {aot_id}: {UNREACHABLE_ROOMS[(stage, room)]}")

    return {key: variant for key, variant in chosen.items() if key not in dropped}


def flag_index(stage, global_id):
    return global_id + (LATE_STAGE_OFFSET if stage >= FIRST_LATE_STAGE else 0)


def room_name(stage, room):
    return ROOM_NAMES.get((stage, room), f"Room {stage}-{room:02X}")


def number_duplicate_names(locations):
    totals = Counter(location["name"] for location in locations)
    seen   = Counter()
    for location in locations:
        base = location["name"]
        if totals[base] > 1:
            seen[base] += 1
            location["name"] = f"{base} {seen[base]}"


def build_locations(chosen):
    locations = []
    for (file, aot_id), (item_type, amount, global_id) in sorted(chosen.items()):
        stage, room = stage_and_room(file)
        locations.append({
            "name": f"{room_name(stage, room)} - {ITEM_NAMES[item_type]}",
            "file": file, "stage": stage, "room": room, "aot_id": aot_id,
            "global_id": global_id, "flag_index": flag_index(stage, global_id), "item_id": item_type, "amount": amount,
        })

    number_duplicate_names(locations)
    return locations


def report_shared_flags(locations):
    names_by_flag = defaultdict(list)
    for location in locations:
        names_by_flag[location["flag_index"]].append(location["name"])

    for index, names in sorted(names_by_flag.items()):
        if len(names) > 1:
            print(f"  SHARED FLAG {index}: {', '.join(names)}")


def write_locations(locations, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(locations, indent=2) + "\n")
    print(f"{len(locations)} locations written to {output_path}")


def parse_flag(text):
    key, value = text.split("=")
    bit_array, index = key.split(",")
    return (int(bit_array), int(index)), int(value)


def main():
    parser = argparse.ArgumentParser(description="Group extracted RE2 item entries into pickup spots")
    parser.add_argument("csv_path")
    parser.add_argument("--flag", action="append", default=[], help="extra known flag, e.g. 0,25=1")
    parser.add_argument("--output", help="write the resolved locations as JSON, e.g. worlds/re2/data/leon_a_locations.json")
    args = parser.parse_args()

    known_flags = {**LEON_A_FLAGS, **dict(parse_flag(text) for text in args.flag)}
    included, review, _excluded = resolve(group_spots(load_rows(args.csv_path)), known_flags)
    locations = build_locations(drop_unreachable(apply_decisions(included, review)))
    report_shared_flags(locations)
    if args.output:
        write_locations(locations, args.output)


if __name__ == "__main__":
    main()