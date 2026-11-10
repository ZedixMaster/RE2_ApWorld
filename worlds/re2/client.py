from __future__ import annotations

from typing import TYPE_CHECKING

import worlds._bizhawk as bizhawk
from NetUtils import ClientStatus
from worlds._bizhawk.client import BizHawkClient

from .catalog import LEON_A_LOCATIONS
from .locations import LOCATION_ID_OFFSET

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

MAIN_RAM = "MainRAM"

FLAG_TABLE_ADDRESS   = 0x09FD38
FLAG_TABLE_SIGNATURE = bytes.fromhex("e47c0c80047d0c80087d0c8060c90c80")

SYSTEM_FLAGS_ADDRESS   = 0x0C7CE4
SCENARIO_FLAGS_ADDRESS = 0x0C7D04
PICKUP_FLAGS_ADDRESS   = 0x0CC9E8
PICKUP_FLAGS_SIZE      = 64

GOAL_FLAG       = 10
NORMAL_FLAG     = 25
CLAIRE_FLAG     = 0
SCENARIO_B_FLAG = 1

RECEIVED_INDEX_ADDRESS = 0x0CCA24
ITEM_BOX_ADDRESS       = 0x0CCB94
ITEM_BOX_SLOTS         = 64
RECORD_SIZE            = 4
EMPTY_RECORD           = bytes(RECORD_SIZE)

INVENTORY_ADDRESS = 0x0CCB68
INVENTORY_SLOTS   = 10

STAGE_AND_ROOM_ADDRESS = 0x0CC948

LIGHTER_SLOT_ADDRESS = 0x0CCB90
LIGHTER_ID           = 0x2F

VANILLA_PICKUPS = {location["flag_index"]: location for location in LEON_A_LOCATIONS}


def flag_is_set(flags: bytes, index: int) -> bool:
    start = (index // 32) * 4
    word  = int.from_bytes(flags[start:start + 4], "little")
    return bool(word & (0x80000000 >> (index % 32)))


def is_leon_a_normal(system_flags: bytes, scenario_flags: bytes) -> bool:
    return (
        flag_is_set(system_flags, NORMAL_FLAG)
        and not flag_is_set(scenario_flags, CLAIRE_FLAG)
        and not flag_is_set(scenario_flags, SCENARIO_B_FLAG)
    )


def slot_record(records: bytes, slot: int) -> bytes:
    return records[slot * RECORD_SIZE:(slot + 1) * RECORD_SIZE]


def find_vanilla_slot(before: bytes, after: bytes, native_id: int, amount: int) -> int | None:
    for slot in range(INVENTORY_SLOTS):
        old_id, old_amount = slot_record(before, slot)[:2]
        new_id, new_amount = slot_record(after, slot)[:2]
        if new_id != native_id:
            continue
        if old_id == 0 and new_amount == amount:
            return slot
        if old_id == native_id and new_amount - old_amount == amount:
            return slot

    return None


def vanilla_items(location: dict) -> list[tuple[int, int]]:
    return [(location["item_id"], location["amount"]), *map(tuple, location.get("alternate_items", []))]


def find_any_vanilla_slot(before: bytes, after: bytes, location: dict) -> int | None:
    for native_id, amount in vanilla_items(location):
        slot = find_vanilla_slot(before, after, native_id, amount)
        if slot is not None:
            return slot

    return None


class RE2Client(BizHawkClient):
    game         = "Resident Evil 2"
    system       = "PSX"
    patch_suffix = None

    def __init__(self) -> None:
        super().__init__()
        self.previous_pickup_flags: bytes | None = None
        self.previous_inventory: bytes | None = None
        self.previous_room: tuple[int, int] | None = None

    async def validate_rom(self, ctx: BizHawkClientContext) -> bool:
        try:
            signature = (await bizhawk.read(ctx.bizhawk_ctx, [
                (FLAG_TABLE_ADDRESS, len(FLAG_TABLE_SIGNATURE), MAIN_RAM),
            ]))[0]
        except bizhawk.RequestFailedError:
            return False

        if signature != FLAG_TABLE_SIGNATURE:
            return False

        ctx.game           = self.game
        ctx.items_handling = 0b111
        ctx.want_slot_data = True

        return True

    async def game_watcher(self, ctx: BizHawkClientContext) -> None:
        if ctx.server is None or ctx.server.socket.closed or ctx.slot_data is None:
            return

        system_flags, scenario_flags, pickup_flags, inventory, stage_and_room, lighter_slot = await bizhawk.read(
            ctx.bizhawk_ctx, [
                (SYSTEM_FLAGS_ADDRESS, 4, MAIN_RAM),
                (SCENARIO_FLAGS_ADDRESS, 4, MAIN_RAM),
                (PICKUP_FLAGS_ADDRESS, PICKUP_FLAGS_SIZE, MAIN_RAM),
                (INVENTORY_ADDRESS, INVENTORY_SLOTS * RECORD_SIZE, MAIN_RAM),
                (STAGE_AND_ROOM_ADDRESS, 4, MAIN_RAM),
                (LIGHTER_SLOT_ADDRESS, 1, MAIN_RAM),
            ],
        )
        current_room = (stage_and_room[0], stage_and_room[2])

        in_game = lighter_slot[0] == LIGHTER_ID
        if not in_game or not is_leon_a_normal(system_flags, scenario_flags):
            self.previous_pickup_flags = None
            self.previous_inventory = None
            self.previous_room = None
            return

        await self.remove_vanilla_items(ctx, pickup_flags, inventory, current_room)
        self.previous_pickup_flags = pickup_flags
        self.previous_inventory = inventory
        self.previous_room = current_room

        new_checks = {
            LOCATION_ID_OFFSET + index
            for index in range(PICKUP_FLAGS_SIZE * 8)
            if flag_is_set(pickup_flags, index)
        } & ctx.missing_locations

        if new_checks:
            await ctx.send_msgs([{"cmd": "LocationChecks", "locations": list(new_checks)}])

        if not ctx.finished_game and flag_is_set(system_flags, GOAL_FLAG):
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True

        await self.deliver_next_item(ctx)

    async def deliver_next_item(self, ctx: BizHawkClientContext) -> None:
        index_bytes, box = await bizhawk.read(ctx.bizhawk_ctx, [
            (RECEIVED_INDEX_ADDRESS, 2, MAIN_RAM),
            (ITEM_BOX_ADDRESS, ITEM_BOX_SLOTS * RECORD_SIZE, MAIN_RAM),
        ])

        received_index = int.from_bytes(index_bytes, "little")
        if received_index >= len(ctx.items_received):
            return

        empty_slot = next(
            (slot for slot in range(ITEM_BOX_SLOTS) if slot_record(box, slot) == EMPTY_RECORD),
            None,
        )

        if empty_slot is None:
            return

        native_id, amount = divmod(ctx.items_received[received_index].item, 1000)
        slot_address      = ITEM_BOX_ADDRESS + empty_slot * RECORD_SIZE

        await bizhawk.guarded_write(
            ctx.bizhawk_ctx,
            [
                (slot_address, [native_id, amount, 0, 0], MAIN_RAM),
                (RECEIVED_INDEX_ADDRESS, (received_index + 1).to_bytes(2, "little"), MAIN_RAM),
            ],
            [
                (RECEIVED_INDEX_ADDRESS, index_bytes, MAIN_RAM),
                (slot_address, EMPTY_RECORD, MAIN_RAM),
            ],
        )

    async def remove_vanilla_items(
        self, ctx: BizHawkClientContext, pickup_flags: bytes, inventory: bytes, current_room: tuple[int, int]
    ) -> None:
        if self.previous_pickup_flags is None or self.previous_inventory is None:
            return
        if self.previous_room != current_room:
            return

        for index, location in VANILLA_PICKUPS.items():
            if flag_is_set(self.previous_pickup_flags, index) or not flag_is_set(pickup_flags, index):
                continue
            if (location["stage"], location["room"]) != current_room:
                continue

            slot = find_any_vanilla_slot(self.previous_inventory, inventory, location)
            if slot is None:
                continue

            slot_address = INVENTORY_ADDRESS + slot * RECORD_SIZE
            await bizhawk.guarded_write(
                ctx.bizhawk_ctx,
                [(slot_address, slot_record(self.previous_inventory, slot), MAIN_RAM)],
                [(slot_address, slot_record(inventory, slot), MAIN_RAM)],
            )