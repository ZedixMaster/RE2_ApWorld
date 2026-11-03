import argparse
import csv
import io
import json
import struct

import pycdlib

RDT_DIRECTORY         = "/PL0/RDT"
OFFSET_TABLE_POSITION = 8
OFFSET_TABLE_COUNT    = 23
SCRIPT_SECTIONS       = {"init": 16, "main": 17}

ITEM_AOT_SET           = 0x4E
ITEM_AOT_SET_4P        = 0x69
ITEM_AOT_SET_FORMAT    = struct.Struct("<6B4h3H2B")
ITEM_AOT_SET_4P_FORMAT = struct.Struct("<6B8h3H2B")

IF_START          = 0x06
ELSE_START        = 0x07
END_IF            = 0x08
CONDITION_OPCODES = {0x21: "ck", 0x23: "cmp"}

GOSUB     = 0x18
EVT_EXEC  = 0x04
AOT_SET   = 0x2C
SCE_EVENT = 5

INSTRUCTION_SIZES = [
    1, 2, 1, 4, 4, 2, 4, 4, 1, 4, 3, 1, 1, 6, 2, 4,
    2, 4, 2, 4, 6, 2, 2, 6, 2, 2, 2, 6, 1, 4, 1, 1,
    1, 4, 4, 6, 4, 3, 6, 4, 1, 2, 1, 6, 20, 38, 3, 4,
    1, 1, 8, 8, 4, 3, 12, 4, 3, 8, 16, 32, 2, 3, 6, 4,
    8, 10, 1, 4, 22, 5, 10, 2, 16, 8, 2, 3, 5, 22, 22, 4,
    4, 6, 6, 6, 22, 6, 4, 8, 4, 4, 2, 2, 3, 2, 2, 2,
    14, 4, 2, 1, 16, 2, 1, 28, 40, 30, 6, 4, 1, 4, 6, 2,
    1, 1, 16, 8, 4, 22, 3, 4, 6, 1, 16, 16, 6, 6, 6, 6,
    2, 3, 3, 1, 2, 6, 1, 1, 3, 1, 6, 6, 8, 24, 24,
]


def read_rdt_files(iso_path):
    iso = pycdlib.PyCdlib()
    iso.open(iso_path)
    try:
        for _directory, _subdirectories, filenames in iso.walk(iso_path=RDT_DIRECTORY):
            for filename in sorted(filenames):
                buffer = io.BytesIO()
                iso.get_file_from_iso_fp(buffer, iso_path=f"{RDT_DIRECTORY}/{filename}")
                yield filename, buffer.getvalue()
    finally:
        iso.close()


def section(data, index):
    offsets = struct.unpack_from(f"<{OFFSET_TABLE_COUNT}I", data, OFFSET_TABLE_POSITION)
    start   = offsets[index]
    end     = min([offset for offset in offsets if offset > start] + [len(data)])

    return data[start:end]


def procedures(script):
    count  = struct.unpack_from("<H", script, 0)[0] // 2
    starts = struct.unpack_from(f"<{count}H", script, 0)
    ends   = starts[1:] + (len(script),)

    return [script[start:end] for start, end in zip(starts, ends)]


class ScriptParseError(Exception):
    pass


def instructions(procedure):
    position = 0
    while position < len(procedure):
        opcode = procedure[position]
        size   = INSTRUCTION_SIZES[opcode] if opcode < len(INSTRUCTION_SIZES) else 0
        if size == 0 or position + size > len(procedure):
            raise ScriptParseError(f"opcode 0x{opcode:02X} at byte {position} of {len(procedure)}")

        yield position, procedure[position:position + size]
        position += size


def called_procedure(instruction):
    if instruction[0] == GOSUB:
        return instruction[1]
    if instruction[0] == EVT_EXEC and instruction[2] == GOSUB:
        return instruction[3]
    if instruction[0] == AOT_SET and instruction[2] == SCE_EVENT and instruction[16] == GOSUB:
        return instruction[17]
    return None


def reachable_procedures(script_procedures):
    reached = set()
    pending = [0]
    while pending:
        number = pending.pop()
        if number in reached or number >= len(script_procedures):
            continue

        reached.add(number)
        try:
            for _position, instruction in instructions(script_procedures[number]):
                target = called_procedure(instruction)
                if target is not None:
                    pending.append(target)
        except ScriptParseError:
            pass

    return reached


def decode_item(instruction):
    (_opcode, aot_id, _sce, _sat, _floor, _super, x, y, width, height, item_type, amount, global_id, md1, action) = ITEM_AOT_SET_FORMAT.unpack(instruction)

    return {
        "aot_id": aot_id, "item_type": f"0x{item_type:02X}", "amount": amount,
        "global_id": global_id, "md1": md1, "action": action,
        "x": x, "y": y, "width": width, "height": height,
    }


def decode_item_4p(instruction):
    fields = ITEM_AOT_SET_4P_FORMAT.unpack(instruction)
    item_type, amount, global_id, md1, action = fields[14:]
    return {
        "aot_id": fields[1], "item_type": f"0x{item_type:02X}", "amount": amount, "global_id": global_id, "md1": md1, "action": action
    }


def room_from_filename(filename):
    name = filename.split(";")[0]
    return int(name[4], 16) - 1, int(name[5:7], 16)


def describe_condition(instruction):
    arguments = ",".join(str(value) for value in instruction[1:])
    return f"{CONDITION_OPCODES[instruction[0]]}({arguments})"


def active_conditions(blocks):
    parts = []
    for block in blocks:
        if not block["conditions"]:
            continue

        joined = " && ".join(describe_condition(condition) for condition in block["conditions"])
        parts.append(f"!({joined})" if block["negated"] else joined)

    return " && ".join(parts)


def condition_blocks(blocks):
    return [
        {"negated": block["negated"], "checks": [[CONDITION_OPCODES[check[0]], *check[1:]] for check in block["conditions"]]}
        for block in blocks if block["conditions"]
    ]


def items_with_conditions(procedure):
    blocks     = []
    collecting = False
    for position, instruction in instructions(procedure):
        blocks = [block for block in blocks if block["end"] is None or position < block["end"]]
        opcode = instruction[0]

        if collecting and opcode in CONDITION_OPCODES:
            blocks[-1]["conditions"].append(instruction)
            continue

        collecting = False

        if opcode == IF_START:
            blocks.append({"conditions": [], "negated": False, "end": None})
            collecting = True
        elif opcode == ELSE_START and blocks:
            blocks[-1]["negated"] = True
            blocks[-1]["end"]     = position + struct.unpack_from("<H", instruction, 2)[0]
        elif opcode == END_IF and blocks:
            blocks.pop()
        elif opcode in (ITEM_AOT_SET, ITEM_AOT_SET_4P):
            yield instruction, active_conditions(blocks), condition_blocks(blocks)


FIELDNAMES = [
    "file", "stage", "room", "script", "procedure", "reachable", "opcode", "aot_id", "item_type", "amount", "global_id", "md1", "action", "x", "y", "width", "height", "conditions", "condition_json", "raw"
]


def extract(iso_path, csv_path):
    rows     = []
    problems = []
    for filename, data in read_rdt_files(iso_path):
        stage, room = room_from_filename(filename)
        for script_name, index in SCRIPT_SECTIONS.items():
            script_procedures = procedures(section(data, index))
            reachable         = reachable_procedures(script_procedures)
            for procedure_index, procedure in enumerate(script_procedures):
                location = {
                    "file": filename.split(";")[0], "stage": stage, "room": f"0x{room:02X}", "script": script_name,
                    "procedure": procedure_index, "reachable": procedure_index in reachable,
                }
                try:
                    for instruction, conditions, blocks in items_with_conditions(procedure):
                        decoded = decode_item(instruction) if instruction[0] == ITEM_AOT_SET else decode_item_4p(instruction)
                        rows.append({
                            **location, "opcode": f"0x{instruction[0]:02X}", **decoded,
                            "conditions": conditions, "condition_json": json.dumps(blocks), "raw": instruction.hex(" ")
                        })
                except ScriptParseError as error:
                    problems.append(f"{location['file']} {script_name} procedure {procedure_index}: {error}")

    with open(csv_path, "w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    return rows, problems


def main():
    parser = argparse.ArgumentParser(description="Extract ITEM_AOT_SET entries from every RE2 room file on the disc")
    parser.add_argument("iso_path")
    parser.add_argument("csv_path")
    args = parser.parse_args()

    rows, problems = extract(args.iso_path, args.csv_path)
    print(f"{len(rows)} item entries written to {args.csv_path}")
    print(f"{len(problems)} procedures could not be fully parsed:")
    for problem in problems:
        print(f"  {problem}")


if __name__ == "__main__":
    main()