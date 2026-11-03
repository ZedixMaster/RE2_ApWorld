# Resident Evil 2 Setup Guide

## Required Software

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases/latest)
- [BizHawk](https://tasvideos.org/BizHawk/ReleaseHistory) 2.11.1 or newer, using the Nymashock PlayStation core
- A disc image of Resident Evil 2 (USA), Disc 1 (Leon), serial SLUS-00421
- The Resident Evil 2 apworld

## Installation

1. Install Archipelago.
2. Double-click the `re2.apworld` file to install it, or copy it into the `custom_worlds` folder of your Archipelago
   installation.
3. Set up a PlayStation BIOS in BizHawk if you have not already.

## Joining a Multiworld Game

1. Start a new game in BizHawk: Leon, scenario A, Normal difficulty.
2. Open the Archipelago Launcher and start the **BizHawk Client**.
3. In BizHawk, open **Tools > Lua Console** and load `connector_bizhawk_generic.lua` from the `data/lua` folder of
   your Archipelago installation.
4. In the BizHawk Client, connect to the server address and enter your slot name.

## Notes

- The client only sends checks while you are playing Leon A on Normal difficulty.
- Received items go to the item box, and your progress is stored in your save file. Loading an older save makes the
  client deliver any items received after that save again.