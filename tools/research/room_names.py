# Keyed by (stage byte, room byte). Names from Evil Resource's RE2 maps, matched by each room's doors and items.
# Some room files cover two Evil Resource rooms; those get both names.
ROOM_NAMES = {
    (0, 0x00): "West Street", (0, 0x01): "Kendo Gun Shop", (0, 0x02): "Basketball Yard",
    (0, 0x03): "R.P.D. Courtyard", (0, 0x04): "East Street", (0, 0x05): "R.P.D. Backyard",
    (0, 0x06): "Outside Shed", (0, 0x07): "Station Yard", (0, 0x08): "Helipad",
    (0, 0x09): "Crow Passage", (0, 0x0A): "Helicopter Corridor", (0, 0x0B): "Storage Room",
    (0, 0x0C): "West Stairway 2F", (0, 0x0D): "Stuffed Tiger Corridor", (0, 0x0E): "Taxidermy Display Room",
    (0, 0x0F): "Waiting Room 2F", (0, 0x10): "Main Hall 2F", (0, 0x11): "Cog Room",
    (0, 0x12): "Library", (0, 0x13): "Lounge", (0, 0x14): "Office Corridor",
    (0, 0x15): "S.T.A.R.S. Office", (0, 0x16): "East Stairway 2F", (0, 0x17): "Main Hall 3F",
    (0, 0x18): "Back Alley", (0, 0x19): "Crashed Bus Area", (0, 0x1A): "Bus",
    (0, 0x1B): "Courtyard Boulevard",

    (1, 0x00): "Main Hall", (1, 0x01): "Waiting Room 1F", (1, 0x02): "West Office",
    (1, 0x03): "File Storage", (1, 0x04): "'L' Corridor", (1, 0x05): "Winding Corridor",
    (1, 0x06): "Operations Room", (1, 0x07): "West Stairway 1F", (1, 0x08): "Dark Room",
    (1, 0x09): "Evidence Room", (1, 0x0A): "East Hallway", (1, 0x0B): "East Office / East Stairway 1F",
    (1, 0x0C): "Interrogation Corridor", (1, 0x0D): "Press Room", (1, 0x0E): "Interrogation Room / Observation Room",
    (1, 0x0F): "Watchman's Corridor", (1, 0x10): "Watchman's Room", (1, 0x11): "Basement Entrance",
    (1, 0x12): "Outside Area", (1, 0x13): "Generator Room", (1, 0x14): "Arms Storage",
    (1, 0x15): "Autopsy Room", (1, 0x16): "Parking Lot", (1, 0x19): "Cell Block Entrance",
    (1, 0x1A): "Kennel", (1, 0x1B): "Chief Irons' Office",

    (2, 0x00): "Taxidermy Room", (2, 0x01): "Cells", (2, 0x02): "Underground Area",
    (2, 0x03): "Septic Pool Walkway", (2, 0x04): "Filtering Room", (2, 0x05): "Cesspool Walkway",
    (2, 0x06): "Cesspool", (2, 0x07): "Construction Area / Construction Storage", (2, 0x08): "Secret Underground Passage",
    (2, 0x09): "Cavernous Walkway", (2, 0x0A): "Sewer Entrance", (2, 0x0B): "Septic Pool Entrance",
    (2, 0x0C): "Storeroom West", (2, 0x0D): "Storeroom East",

    (3, 0x00): "Sewer South Passage", (3, 0x01): "Control Room 1 / Warehouse 1", (3, 0x02): "Sewer North Passage",
    (3, 0x03): "Control Room 2 / Warehouse 2", (3, 0x04): "'T' Corridor", (3, 0x05): "Sewer Passage 1",
    (3, 0x07): "Sewer Passage 2", (3, 0x08): "Water Pool", (3, 0x09): "Upper Walkway",
    (3, 0x0A): "Service Tunnel", (3, 0x0B): "Ventilation Tunnel", (3, 0x0C): "Garbage Area",
    (3, 0x0D): "Electric Service Tunnel", (3, 0x0E): "Sewer Exit", (3, 0x0F): "Small Ventilation Tunnel",
    (3, 0x10): "Dumping Area",

    (4, 0x00): "Cable Car", (4, 0x01): "Cable Car Platform", (4, 0x02): "Factory Tunnel 1",
    (4, 0x03): "Turntable Control Room", (4, 0x04): "Turntable Yard", (4, 0x05): "Turntable Cabin",
    (4, 0x06): "Turntable Yard (Turntable Lowered)", (4, 0x07): "Hydrolic Monitor Room", (4, 0x08): "Factory Tunnel 2",
    (4, 0x09): "Turntable Cabin (Descending)",

    (5, 0x00): "Turntable Yard (Laboratory)", (5, 0x01): "Elevator", (5, 0x02): "Elevator Corridor",
    (5, 0x03): "Steam Room", (5, 0x04): "Power Room", (5, 0x05): "Smelting Room",
    (5, 0x06): "Elevator Area", (5, 0x07): "Security Room", (5, 0x08): "Main Shaft",
    (5, 0x09): "Sleeping Quarters B", (5, 0x0A): "Sleeping Quarters A", (5, 0x0B): "West Area",
    (5, 0x0C): "East Area", (5, 0x0D): "Cold Room", (5, 0x0E): "Level 4 Walkway",
    (5, 0x0F): "Culture Experiment Room", (5, 0x10): "Active Treatment Experimentation Room", (5, 0x11): "Main Shaft (Lower)",
    (5, 0x12): "Monitor Room", (5, 0x13): "Computer Room", (5, 0x14): "Lab Entry Corridor",
    (5, 0x15): "P-4 Laboratory", (5, 0x16): "Level 5 Walkway / Central Corridor", (5, 0x17): "Laboratory Cargo Room",

    (6, 0x00): "Gate Platform", (6, 0x01): "Main Platform", (6, 0x02): "Power Control Platform",
    (6, 0x03): "Train Front Carriage", (6, 0x04): "Train Rear Carriage",
}
