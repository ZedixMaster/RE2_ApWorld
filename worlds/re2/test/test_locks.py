from . import RE2TestBase

AFTER_PLUG_PANEL = ("Sewers", "Sewers Water Pool Side", "Factory", "Laboratory", "Laboratory B5", "Computer Room",
                    "Active Treatment Room", "Cargo Room", "Gate Platform")

AFTER_BASEMENT = ("Sewage Disposal", "Ada Sewage Disposal", *AFTER_PLUG_PANEL)

PLUGS = ("Bishop Plug", "Rook Plug", "King Plug", "Jaguar Stone (R)")

MEDALS = ("Eagle Medal", "Wolf Medal")


class TestKeyDoors(RE2TestBase):
    def test_spade_key(self):
        self.assertAccessDependency(self.locations_in("File Storage", "RPD 2F", "Rooftop", "Storage Room"),
                                    [["Spade Key x2"]])

    def test_diamond_key(self):
        self.assertAccessDependency(self.locations_in("Evidence Room", "West Office", "Interrogation Room"),
                                    [["Diamond Key x2"]])

    def test_heart_key(self):
        self.assertAccessDependency(self.locations_in("RPD Basement", "Watchman's Room", "Autopsy Room", "Arms Storage",
                                                      *AFTER_BASEMENT),
                                    [["Heart Key"]])

    def test_club_key(self):
        self.assertAccessDependency(self.locations_in("Press Room", "Watchman's Room", "Autopsy Room"),
                                    [["Club Key x3"]])

    def test_valve_handle(self):
        self.assertAccessDependency(self.locations_in("Storage Room", "Sewers Water Pool Side"),
                                    [["Valve Handle"]])

    def test_red_card_key(self):
        self.assertAccessDependency(self.locations_in("Arms Storage"), [["Red Card Key"]])

    def test_manhole_opener(self):
        self.assertAccessDependency(self.locations_in(*AFTER_BASEMENT), [["Manhole Opener"]])

    def test_down_key(self):
        self.assertAccessDependency(self.locations_in("Laboratory", "Laboratory B5", "Computer Room",
                                                      "Active Treatment Room", "Cargo Room", "Gate Platform"),
                                    [["Down Key"]])

    def test_main_fuse(self):
        self.assertAccessDependency(self.locations_in("Laboratory B5", "Computer Room", "Cargo Room", "Gate Platform"),
                                    [["Main Fuse"]])

    def test_umbrella_key_card(self):
        self.assertAccessDependency(self.locations_in("Computer Room", "Active Treatment Room"),
                                    [["Umbrella Key Card x2"]])

    def test_mo_disk(self):
        self.assertAccessDependency(self.locations_in("Cargo Room", "Gate Platform"), [["MO Disk"]])


class TestMultiItemLocks(RE2TestBase):
    def test_every_plug_is_needed(self):
        for plug in PLUGS:
            with self.subTest(plug=plug):
                state = self.state_without(plug)
                self.assertFalse(state.can_reach_region("Sewers", self.player))

    def test_all_plugs_open_the_sewers(self):
        self.assertAccessDependency(self.locations_in(*AFTER_PLUG_PANEL), [list(PLUGS)])

    def test_king_plug_needs_both_red_jewels(self):
        state = self.state_without("Red Jewel")

        first_jewel, second_jewel = self.get_items_by_name("Red Jewel")

        state.collect(first_jewel)
        self.assertFalse(state.can_reach_location("Storage Room - King Plug", self.player))

        state.collect(second_jewel)
        self.assertTrue(state.can_reach_location("Storage Room - King Plug", self.player))

    def test_every_medal_is_needed(self):
        for medal in MEDALS:
            with self.subTest(medal=medal):
                self.assertFalse(self.state_without(medal).can_reach_region("Factory", self.player))


class TestGoal(RE2TestBase):
    def test_beatable_with_everything(self):
        self.assertTrue(self.multiworld.can_beat_game(self.state_without()))

    def test_goal_needs_each_story_key(self):
        for item in ("Umbrella Key Card x2", "MO Disk", "Main Fuse", "Down Key", "Manhole Opener", "Heart Key"):
            with self.subTest(item=item):
                self.assertFalse(self.multiworld.can_beat_game(self.state_without(item)))