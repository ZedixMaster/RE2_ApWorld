local DOMAIN = "MainRAM"
local MAX_PRINT = 100

local size = memory.getmemorydomainsize(DOMAIN)
local snaps = {}
local pending = nil

local form = forms.newform(250, 150, "Room ID Finder")
local labelBox = forms.textbox(form, "A", 100, 20, nil, 10, 10)
forms.button(form, "Snapshot", function() pending = "snap" end, 120, 8, 110, 24)
forms.button(form, "Analyze", function() pending = "analyze" end, 10, 45, 100, 24)
forms.button(form, "Reset", function() pending = "reset" end, 120, 45, 110, 24)
local status = forms.label(form, "0 snapshots", 10, 80, 220, 20)

local function update_status()
  local text = #snaps .. " snapshots:"
  for _, s in ipairs(snaps) do text = text .. " " .. s.label end
  forms.settext(status, text)
end

local function snapshot()
  local label = forms.gettext(labelBox)
  if label == "" then
    console.log("Enter a room label first.")
    return
  end
  -- 1-indexed: data[i] is the byte at address i - 1
  local data = memory.read_bytes_as_array(0, size, DOMAIN)
  snaps[#snaps + 1] = { label = label, data = data }
  console.log(string.format("Snapshot %d taken in room '%s'.", #snaps, label))
  update_status()
end

local function analyze()
  local labels, groups = {}, {}
  for _, s in ipairs(snaps) do
    if not groups[s.label] then
      groups[s.label] = {}
      labels[#labels + 1] = s.label
    end
    table.insert(groups[s.label], s.data)
  end

  if #labels < 2 then
    console.log("Need snapshots from at least 2 different rooms.")
    return
  end
  local revisited = false
  for _, label in ipairs(labels) do
    if #groups[label] > 1 then revisited = true end
  end
  if not revisited then
    console.log("Warning: no room was snapshotted twice; results will be noisy.")
  end

  local hits = {}
  local vals = {}
  for i = 1, size do
    local ok = true
    for j = 1, #labels do
      local g = groups[labels[j]]
      local v = g[1][i]
      for k = 2, #g do
        if g[k][i] ~= v then ok = false break end
      end
      if not ok then break end
      for p = 1, j - 1 do
        if vals[p] == v then ok = false break end
      end
      if not ok then break end
      vals[j] = v
    end
    if ok then hits[#hits + 1] = i end
  end

  console.log(string.format("%d candidate addresses (rooms: %s).", #hits, table.concat(labels, ", ")))
  for n = 1, math.min(#hits, MAX_PRINT) do
    local i = hits[n]
    local parts = {}
    for _, label in ipairs(labels) do
      parts[#parts + 1] = string.format("%s=%02X", label, groups[label][1][i])
    end
    console.log(string.format("0x%06X  %s", i - 1, table.concat(parts, "  ")))
  end
  if #hits > MAX_PRINT then
    console.log(string.format("... %d more not shown.", #hits - MAX_PRINT))
  end
end

event.onexit(function() forms.destroy(form) end)

while true do
  if pending == "snap" then
    snapshot()
  elseif pending == "analyze" then
    analyze()
  elseif pending == "reset" then
    snaps = {}
    update_status()
    console.log("Snapshots cleared.")
  end
  pending = nil
  emu.frameadvance()
end
