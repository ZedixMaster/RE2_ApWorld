from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld


class RE2WebWorld(WebWorld):
    game  = "Resident Evil 2"
    theme = "stone"

    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Resident Evil 2 (PS1) on BizHawk for Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Bossus"],
    )

    tutorials = [setup_en]