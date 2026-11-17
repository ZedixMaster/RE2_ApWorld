local DOMAIN = "MainRAM"

local SCRIPT_DIR = debug.getinfo(1, "S").source:match("^@(.*[/\\])") or ""
local REPO_ROOT = SCRIPT_DIR .. "../../"
local LOG_PATH = SCRIPT_DIR .. "ram_log_" .. os.date("%Y%m%d_%H%M%S") .. ".txt"

local INVENTORY_ADDRESS = 0x0CCB68
local INVENTORY_SLOTS = 10
local LIGHTER_SLOT_ADDRESS = 0x0CCB90
local ITEM_BOX_ADDRESS = 0x0CCB94
local ITEM_BOX_SLOTS = 64
local RECORD_SIZE = 4

local PICKUP_ARRAYS = { [8] = 0, [34] = 256 }
local RECEIVED_INDEX_ADDRESS = 0x0CCA24

local FLAG_ARRAYS = {
  { array = 30, base = 0x0C7CE0, size = 0x04 },
  { array = 0,  base = 0x0C7CE4, size = 0x20 },
  { array = 1,  base = 0x0C7D04, size = 0x04 },
  { array = 2,  base = 0x0C7D08, size = 0x04 },
  { array = 10, base = 0x0C7D0C, size = 0x14 },
  { array = 12, base = 0x0C7D20, size = 0x20 },
  { array = 3,  base = 0x0CC960, size = 0x20 },
  { array = 4,  base = 0x0CC980, size = 0x20 },
  { array = 5,  base = 0x0CC9A0, size = 0x08 },
  { array = 6,  base = 0x0CC9A8, size = 0x20 },
  { array = 7,  base = 0x0CC9C8, size = 0x20 },
  { array = 8,  base = 0x0CC9E8, size = 0x20 },
  { array = 34, base = 0x0CCA08, size = 0x1C },
  { array = 35, base = 0x0CCA34, size = 0x04 },
  { array = 9,  base = 0x0CCA38, size = 0x14 },
  { array = 32, base = 0x0CCA4C, size = 0x04 },
  { array = 33, base = 0x0CCA50, size = 0x04 },
  { array = 31, base = 0x0CCB60, size = 0x08 },
}
for array = 13, 29 do
  FLAG_ARRAYS[#FLAG_ARRAYS + 1] = { array = array, base = 0x0CCA54 + (array - 13) * 0x10, size = 0x10 }
end

local SCALARS = {
  { label = "stage",           address = 0x0CC948, size = 1 },
  { label = "next room",       address = 0x0CC94A, size = 1 },
  { label = "loaded room",     address = 0x0CC35C, size = 1 },
  { label = "last item",       address = 0x0CC35D, size = 1 },
  { label = "transition",      address = 0x0C646C, size = 2 },
  { label = "AP received idx", address = RECEIVED_INDEX_ADDRESS, size = 2 },
}

local NOISY_AFTER = 40

local function read_file(path)
  local file = io.open(path, "r")
  if not file then return nil end
  local text = file:read("*a")
  file:close()
  return text
end

local function load_item_names()
  local names = {}
  local text = read_file(REPO_ROOT .. "worlds/re2/items.py") or ""
  for hex, name in text:gmatch('0x(%x%x): "([^"]+)"') do
    names[tonumber(hex, 16)] = name
  end
  return names
end

local function load_pickup_names()
  local names = {}
  local text = read_file(REPO_ROOT .. "worlds/re2/data/leon_a_locations.json") or ""
  local current = {}
  for line in text:gmatch("[^\n]+") do
    local name = line:match('"name": "([^"]+)"')
    if name then current = { name = name } end
    local stage = line:match('"stage": (%d+)')
    if stage then current.stage = tonumber(stage) end
    local room = line:match('"room": (%d+)')
    if room then current.room = tonumber(room) end
    local flag = line:match('"flag_index": (%d+)')
    if flag then
      flag = tonumber(flag)
      names[flag] = names[flag] or {}
      table.insert(names[flag], string.format("%s [%d-%02X]", current.name, current.stage, current.room))
    end
  end
  return names
end

local ITEM_NAMES = load_item_names()
local PICKUP_NAMES = load_pickup_names()

local log_file = io.open(LOG_PATH, "w")

local function log(text)
  local line = string.format("[%7d] %s", emu.framecount(), text)
  console.log(line)
  if log_file then
    log_file:write(line, "\n")
    log_file:flush()
  end
end

local function read(address, size)
  return memory.read_bytes_as_array(address, size, DOMAIN)
end

local function describe_record(bytes, offset)
  local id, amount = bytes[offset], bytes[offset + 1]
  local raw = string.format("%02X %02X %02X %02X", id, amount, bytes[offset + 2], bytes[offset + 3])
  if id == 0 then return raw .. " (empty)" end
  return string.format("%s (%s x%d)", raw, ITEM_NAMES[id] or "unknown", amount)
end

local function flag_index(byte_offset, bit)
  return (byte_offset // 4) * 32 + 31 - ((byte_offset % 4) * 8 + bit)
end

local change_counts = {}

local function is_muted(key)
  change_counts[key] = (change_counts[key] or 0) + 1
  if change_counts[key] == NOISY_AFTER then
    log(string.format("MUTED %s: changed %d times, probably a timer or per-frame value", key, NOISY_AFTER))
  end
  return change_counts[key] >= NOISY_AFTER
end

local function report_flag_changes(entry, old, new)
  for offset = 1, entry.size do
    local changed = old[offset] ~ new[offset]
    if changed ~= 0 and not is_muted(string.format("array %d byte %d", entry.array, offset - 1)) then
      for bit = 0, 7 do
        if changed & (1 << bit) ~= 0 then
          local index = flag_index(offset - 1, bit)
          local state = (new[offset] & (1 << bit) ~= 0) and "SET  " or "CLEAR"
          local line = string.format("FLAG %s ck(%d,%d)  0x%06X bit 0x%02X",
            state, entry.array, index, entry.base + offset - 1, 1 << bit)
          local pickup_offset = PICKUP_ARRAYS[entry.array]
          if pickup_offset then
            local pickup = index + pickup_offset
            local names = PICKUP_NAMES[pickup]
            line = line .. string.format("  pickup flag %d: %s", pickup, names and table.concat(names, " | ") or "not in catalog")
          end
          log(line)
        end
      end
    end
  end
end

local function report_record_changes(label, base, slots, old, new)
  for slot = 0, slots - 1 do
    local offset = slot * RECORD_SIZE + 1
    for i = 0, RECORD_SIZE - 1 do
      if old[offset + i] ~= new[offset + i] then
        log(string.format("%s slot %d (0x%06X): %s -> %s", label, slot + 1, base + slot * RECORD_SIZE,
          describe_record(old, offset), describe_record(new, offset)))
        break
      end
    end
  end
end

local function read_scalar(scalar)
  if scalar.size == 2 then return memory.read_u16_le(scalar.address, DOMAIN) end
  return memory.read_u8(scalar.address, DOMAIN)
end

local function log_position()
  log(string.format("POSITION x=%d y=%d z=%d",
    memory.read_s32_le(0x0C7D5C, DOMAIN), memory.read_s32_le(0x0C7D60, DOMAIN), memory.read_s32_le(0x0C7D64, DOMAIN)))
end

local function dump_records(label, base, slots, bytes)
  for slot = 0, slots - 1 do
    local offset = slot * RECORD_SIZE + 1
    if bytes[offset] ~= 0 then
      log(string.format("  %s slot %d (0x%06X): %s", label, slot + 1, base + slot * RECORD_SIZE, describe_record(bytes, offset)))
    end
  end
end

local previous = {}

local function take_snapshot()
  local snapshot = { flags = {}, scalars = {} }
  for i, entry in ipairs(FLAG_ARRAYS) do snapshot.flags[i] = read(entry.base, entry.size) end
  for i, scalar in ipairs(SCALARS) do snapshot.scalars[i] = read_scalar(scalar) end
  snapshot.inventory = read(INVENTORY_ADDRESS, INVENTORY_SLOTS * RECORD_SIZE)
  snapshot.lighter = read(LIGHTER_SLOT_ADDRESS, RECORD_SIZE)
  snapshot.box = read(ITEM_BOX_ADDRESS, ITEM_BOX_SLOTS * RECORD_SIZE)
  return snapshot
end

local function log_state(reason)
  log("STATE " .. reason)
  for i, scalar in ipairs(SCALARS) do
    log(string.format("  %s = 0x%X", scalar.label, previous.scalars[i]))
  end
  log_position()
  dump_records("INV", INVENTORY_ADDRESS, INVENTORY_SLOTS, previous.inventory)
  dump_records("LIGHTER", LIGHTER_SLOT_ADDRESS, 1, previous.lighter)
  dump_records("BOX", ITEM_BOX_ADDRESS, ITEM_BOX_SLOTS, previous.box)
end

local function compare(current)
  for i, entry in ipairs(FLAG_ARRAYS) do
    report_flag_changes(entry, previous.flags[i], current.flags[i])
  end
  local room_changed = false
  for i, scalar in ipairs(SCALARS) do
    if previous.scalars[i] ~= current.scalars[i] and not is_muted(scalar.label) then
      log(string.format("%s: 0x%X -> 0x%X", scalar.label, previous.scalars[i], current.scalars[i]))
      room_changed = room_changed or scalar.label == "loaded room"
    end
  end
  report_record_changes("INV", INVENTORY_ADDRESS, INVENTORY_SLOTS, previous.inventory, current.inventory)
  report_record_changes("LIGHTER", LIGHTER_SLOT_ADDRESS, 1, previous.lighter, current.lighter)
  report_record_changes("BOX", ITEM_BOX_ADDRESS, ITEM_BOX_SLOTS, previous.box, current.box)
  if room_changed then log_position() end
end

local pending_mark, pending_dump = nil, false
local form = forms.newform(300, 110, "RE2 RAM Logger")
local note_box = forms.textbox(form, "", 270, 20, nil, 10, 10)
forms.button(form, "Mark", function() pending_mark = forms.gettext(note_box) end, 10, 40, 130, 24)
forms.button(form, "Dump state", function() pending_dump = true end, 150, 40, 130, 24)

event.onexit(function()
  forms.destroy(form)
  if log_file then log_file:close() end
end)

previous = take_snapshot()
log("Logging to " .. LOG_PATH)
log_state("at start")

while true do
  local current = take_snapshot()
  compare(current)
  previous = current
  if pending_mark then
    log("==== MARK: " .. pending_mark .. " ====")
    pending_mark = nil
  end
  if pending_dump then
    log_state("on request")
    pending_dump = false
  end
  emu.frameadvance()
end
