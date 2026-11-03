# Leon A lock table (draft, 2026-11-03)

Sources:
- `scan_locks.py` (scratchpad, not in the repo yet), run on Disc 1 (SLUS-00421). It reads the room scripts for `DOOR_AOT_SET` key fields, `sce_item_get` (0x76), `sce_item_lost` (0x62) and `keep_item_ck` (0x5E).
- Evil Resource's per-item pages (Leon A, Normal).
- cvxfreak's GameFAQs walkthrough (faqs/21208, Leon A section). It confirmed the route order, the Ada sections and which areas Leon A uses.

Evil Resource / cvxfreak name ↔ our `NATIVE_ITEM_NAMES`: Virgin Heart / "Red Jewel" = Red Jewel (0x33), Gold Cogwheel = Cog (0x4A), Square Crank = Crank (0x43), Weapon Box Key / cvxfreak's "Locker Key" (tram area) = Weapon Storage Key (0x3F), Lab Card Key = Umbrella Key Card (0x61), Brad's Locker Key = Special Key (0x53), cvxfreak's "Control Panel Key" = Down Key (0x5D).

Room name mapping (cvxfreak → Evil Resource): Green Hallway #1/#2 = 'L' Corridor / Winding Corridor; Red Jewel Statue Room = West Stairway 2F; STARS Reception Room = Lounge; Chief's Reception Room = Waiting Room 2F; Bird Hallway = Crow Passage; Fan Room = East Office; Gear Room = Cog Room; H-shaped room = Septic Pool Walkway; Crate Room = Cesspool; Sewer Plant = Cesspool Walkway / Construction Area.

Leon starts with the Knife, Handgun and **Lighter**, so every puzzle that only needs the Lighter is free.

## 1. What the disc scan found

**Door key locks** (`DOOR_AOT_SET` bytes +29 key_id = lock flag, +30 key_type = item; 0xFF = "locked from this side", 0xFE = "opens from this side"):

| Door | Needs | Leon A? |
|---|---|---|
| 'L' Corridor → File Storage | Spade Key | yes |
| Office Corridor → Lounge | Spade Key | yes (A only) |
| West Stairway 1F → Evidence Room | Diamond Key | yes |
| Interrogation Corridor → Interrogation Room | Diamond Key | yes |
| East Office → Watchman's Corridor | Heart Key | yes |
| Interrogation Corridor → Press Room | Club Key | yes |
| Watchman's Corridor → Watchman's Room | Club Key | yes |
| Basement Entrance → Autopsy Room | Club Key | yes |
| East Area → Active Treatment Exp. Room | Umbrella Key Card | yes |
| Lab Entry Corridor → Computer Room | Umbrella Key Card | yes |
| R.P.D. Backyard → Outside Shed | Cabin Key | B only (Backyard unreachable in A) |
| Steam Room → Power Room | Power Room Key | B only |
| Elevator Area → Security Room | Master Key | Leon B only (open in A) |
| Gate Platform → Main Platform | Platform Key | B only |

One-way shortcuts (open from the inner side only): Evidence Room → West Office, Crow Passage → East Stairway 2F, East Hallway → Main Hall, Sleeping Quarters B → West Area. Also the Main Hall 2F emergency ladder down to the Main Hall, and the Cog Room dust chute down to the Cell Block.

**Scripted item gives/removals**: only these, so almost every key item is a normal `ITEM_AOT_SET` pickup that appears once its puzzle is solved:
- `give Blue Card Key` in West Office (Marvin): **not in the catalog**.
- Dark Room: check and remove Special Key (the costume locker).
- P-4 Laboratory: check and remove Weapon Storage Key (the weapons locker).
- Elevator: checks Master Key (B only).

Puzzles that use items up (medal statue, plug panel, waterfall, cog mechanism, card readers) don't appear as script opcodes, so they're probably handled by the exe through item-use AOTs. The logic has to model them from the walkthroughs.

## 2. Lock table (route order)

| # | Lock | Item(s) | Opens / gives | Region gained |
|---|---|---|---|---|
| — | Start | — | City: West Street → Gun Shop (Shotgun from Kendo's body, 2× bullets) → Basketball Yard → Back Alley → Crashed Bus Area → Bus → Courtyard Boulevard → R.P.D. Courtyard | **City** |
| P1 | **PONR**: R.P.D. Courtyard → Main Hall | — | Main Hall, West Office (Blue Card Key from Marvin; Heart Key later, from zombie Marvin's desk) | **RPD Main Hall** |
| 1 | Main Hall computer | Blue Card Key (event, vanilla) | Waiting Room 1F, East Hallway | **RPD 1F West / East** |
| — | (free) | — | 'L' Corridor, Winding Corridor, Operations Room, West Stairway 1F/2F, Dark Room, Office Corridor, S.T.A.R.S. Office (Unicorn Medal, 2nd Shotgun in locker), East Office (safe 2236 from the Police Memorandum: shells + map), East Hallway, Interrogation Corridor | |
| 2 | Operations Room fireplace | Lighter (start) | Red Jewel #1 | |
| 3 | West Stairway 2F statues | — | Red Jewel #2 | |
| 4 | Main Hall maiden statue | Unicorn Medal | Spade Key (pickup) | |
| 5 | Spade doors | Spade Key | File Storage (Crank); Lounge → Library (Bishop Plug, bookcase puzzle), Main Hall 2F/3F, Waiting Room 2F (Small Key), Cog Room lower, Helicopter Corridor (fire side), Crow Passage, Helipad, Station Yard, Outside Shed (Valve Handle) | **RPD 2F** |
| 6 | Lounge locked desk | Small Key | Handgun Parts | |
| 7 | Helipad water tower | Valve Handle (kept, reused in the sewers) | puts out the helicopter fire → Storage Room (Diamond Key, shells) | **Storage Room** |
| 8 | Storage Room statues | Red Jewel ×2 | King Plug | |
| 9 | Diamond doors | Diamond Key | Evidence Room (Film A); Interrogation/Observation Room (Rook Plug, Small Key, Cord) | |
| 10 | Heart door | Heart Key | Watchman's Corridor, Basement Entrance, Generator Room, Outside Area, Arms Storage (door), Parking Lot (Ada, push the truck), Cell Block Entrance, Cells (Manhole Opener, from Ben), Kennel | **RPD Basement** |
| 11 | Kennel manhole | Manhole Opener | Underground Area, Septic Pool Entrance, Septic Pool Walkway (plug panel), Storeroom West | **Sewage Disposal** |
| A1 | **Ada section 1** (starts on leaving the plug room; cvxfreak inserts the King Plug first) | — | Ada: Cesspool Walkway, Construction Area (lift: Shotgun Shells g194), Cesspool (crate puzzle: Club Key g119). Then **Leon** gets two hand-off pickups at Septic Pool Entrance: Club Key g124, Shotgun Shells g193 (g193 only if g194 was picked up) | |
| 12 | Club doors | Club Key | Press Room (Film B; Lighter lamp puzzle → Cog), Watchman's Room (Magnum), Autopsy Room (Red Card Key) | |
| 13 | Cog Room stairs | Crank | Cog Room upper area | |
| 14 | Cog Room gear mechanism | Cog (+13) | Knight Plug | |
| 15 | Arms Storage card reader | Red Card Key + Generator Room switch puzzle (free) | Sub Machinegun, Side Pack (not in the catalog), ammo | |
| 16 | Septic Pool Walkway panel (G-Imago boss on the way) | Bishop + Rook + King + Knight Plug | Filtering Room → Sewer North Passage, Control Room 2/Warehouse 2 (save room; Lighter lamps), 'T' Corridor | **Sewers** |
| A2 | **Ada section 2** (Annette shoots Leon at the lift) | — | Ada follows Annette through the fan tunnel to the sewer control room. No catalog pickups known | |
| — | (free) | — | Sewer Passage 1 (Wolf Medal), Sewer Passage 2 (waterfall). The fan ladder up to the Upper Walkway is blocked while the fan spins | |
| 17 | Water Pool bridge | Valve Handle | Water Pool, Service Tunnel (Alligator boss), Dumping Area, Upper Walkway via ladder (Eagle Medal) | |
| 18 | Sewer Passage 2 waterfall | Wolf Medal + Eagle Medal | Electric Service Tunnel, Sewer Exit → tram | |
| — | Tram (William's arm, Ada fights it). **Two-way**: cvxfreak says you can ride back to the RPD from the factory ("here is your last chance") | — | Cable Car Platform (flare corner: Weapon Storage Key), Factory Tunnel 1 (Shotgun Parts), Factory Tunnel 2, Turntable Control Room (save room), Turntable Yard, Turntable Cabin (Down Key) | **Factory** |
| P2 | **PONR**: turntable/elevator car descent (William II boss) | Down Key | Lab: Turntable Yard, Elevator Corridor, Steam Room, Smelting Room, Elevator, Elevator Area, Security Room, Main Shaft, East Area, Cold Room (Fuse Case), Culture Experiment Room, West Area, Sleeping Quarters A (Flamethrower) + B | **Lab B1–B4** |
| 19 | Cold Room machine | Fuse Case | Main Fuse (catalog pickup g24 → location rule `has Fuse Case`) | |
| 20 | Main Shaft power core | Main Fuse | lab power: the locked shutter, then the ladder down (probably West Area → Level 4 Walkway) | **Lab B5** |
| — | (after power) | — | Level 4 Walkway, Level 5 Walkway/Central Corridor (3 Super Lickers), Monitor Room (save room), Lab Entry Corridor, P-4 Laboratory (Umbrella Key Card) | |
| 21 | P-4 weapons locker | Weapon Storage Key | Magnum Parts | |
| 22 | Lab Entry Corridor card door | Umbrella Key Card | Computer Room (Giant Moth boss; log in as GUEST) | |
| 23 | East Area right shutter + card door | Umbrella Key Card + Computer Room GUEST login (probably what opens the shutter) | fingerprint terminal, Active Treatment Room (MO Disk) → Annette gives the G-Virus → **self-destruct starts** | |
| 24 | Central Corridor MO Disk shutter | MO Disk (during the self-destruct) | Laboratory Cargo Room → elevator (William III/IV) | |
| G | Goal | — | down the elevator → Gate Platform tunnel, ending flag 0x0C7CE6 bit 0x20 | **Victory** |

Things that **aren't progression in Leon A**: Cord (optional shutters), Films A/B/D (they only develop into files), Special Key/Locker Key (costume, and only if you pick up nothing before Brad), G-Virus (Annette event), Side Pack (event).

**Small Key is progression**: it gates the Lounge Handgun Parts (g18).

**Bosses** (for combat logic later): G-Imago at the plug door, Alligator (Service Tunnel; the gas canister makes it easy), William's arm on the tram (Ada can handle it), William II after the turntable descent, Giant Moth in the Computer Room, William III/IV in the Cargo Room elevator.

## 3. Catalog problems this turns up

**Unreachable in Leon A (19 locations): drop them or move them to a B catalog.**
- R.P.D. Backyard: Cabin Key g4 (reached only from East Street, which is the B start). cvxfreak: the Outside Shed back door "only leads back to the fire from the beginning", and Leon A gets there from the roof.
- Chief Irons' Office: Handgun Bullets g2; Stuffed Tiger Corridor: Magnum Rounds g206; Taxidermy Display Room: Crank g106. cvxfreak passes "a blocked door" in the Helicopter Corridor, and Leon A's Crank is in File Storage.
- Control Room 1 / Warehouse 1: 7 items (the 'T' Corridor door goes there only for Claire, `ck(1,0,1)`; Leon goes to Control Room 2)
- Hydrolic Monitor Room: Up Key g9, Shotgun Shells g76 (Turntable Yard Lowered → Monitor Room only when `!ck(1,1,0)`, i.e. B)
- Power Room: Master Key g20 (Power Room Key is B only)
- Main Platform: Joint Plugs g34/g39; Power Control Platform: Rocket Launcher g40; Train Rear Carriage: Ink Ribbon g78, Platform Key g79 (Platform Key is B only)

**Other fixes**
- Blue Card Key isn't a pickup (Marvin gives it). Phase 1: keep it vanilla as an event in Main Hall/West Office. Later: detect the give and turn it into a location.
- Cog Room item 0x39 (g55) is unconditional on the disc, but Evil Resource *and* cvxfreak say it's the Knight Plug, and the panel needs a Knight Plug. **Check in game what actually lands in the inventory.** The AP item placed there must be whatever the panel accepts.
- **Ada's pickups**: g119 (Cesspool Club Key) and g194 (Construction Area shells) are picked up *by Ada*. g124/g193 are Leon's hand-off copies, not duplicates. That's four real checks, but Ada has her own inventory, so the client's vanilla-item removal and the in-game guard (the Lighter slot) need testing during her section.
- Two Shotguns are both real in Leon A: Kendo's (g15) and the S.T.A.R.S. Office locker (g103).
- Dark Room Film D vs S.T.A.R.S. Office Film D: Evil Resource lists only the S.T.A.R.S. Office one.
- Culture Experiment Room Sub Machinegun g30: cvxfreak only mentions the Arms Storage SMG. Probably a B or cross-scenario variant; check.
- `classification()` changes: Films, Cord and Special Key should be filler or useful. Small Key stays progression.

## 4. Verify in game (or with more script reading)

1. Cog Room: Knight Plug vs 0x39.
2. Ada section 1: what triggers it (entering or leaving the plug room, or inserting a plug)? Where does Ada's inventory live in RAM? Do the client's check detection and removal work while she's in control?
3. With randomized items, can key items be used out of story order? Mainly: the plug panel before the G-Imago event, the MO Disk shutter before the self-destruct, the Umbrella Key Card doors before the Computer Room login. Any of these can break the logic even when the item is in hand.
4. Does Outside Area (1-12) ↔ Construction Area (2-07) open for Leon? cvxfreak doesn't use it, but it's Ada's lift area.
5. Confirm that the Main Fuse is what opens the West Area shutter to the Level 4 Walkway.
6. Is the Eagle Medal reachable through the fan ladder once the fan is stopped, or only through the Water Pool bridge (Valve Handle)? Either way it needs the Valve Handle.

Resolved by the walkthrough: Chief's office is not used in Leon A; the tram is two-way; the turntable descent is the mid-game PONR; the Small Key opens the Lounge desk.

Caveat on the scan: the conditions only cover `if` blocks inside the same procedure. A door set inside a procedure that its caller wraps in a condition shows up as unconditional, which is probably why some B-only doors look open.
