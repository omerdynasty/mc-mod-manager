# Mod Folder Manager v1.2
added: automatic detection of mod loader and minecraft version from .jar filenames inside mods folder
added: message when mods are not backed up, including guessed loader and version (e.g. "Mods are not backed up (these seem to be for Fabric 1.19.2)")
added: when mods are already backed up, shows exact backup folder name that matches
changed: get\_mod\_files() now returns only .jar files to avoid irrelevant files
changed: backup comparison uses sorted file lists to ensure correct match regardless of order
changed: all terminal output messages are now in english
---

Mod Folder Manager is a Python tool that helps you backup, manage, and easily restore your Minecraft mods. It allows you to create backups for different mod loaders, versions, and modpacks, simplifying the management of multiple versions, loaders, and modpacks. This tool helps you keep your mods organized and secure, making it easier to restore your preferred mod setups.

## Features

- **Mod Backup**: Backup your mods with a specific mod loader, version, and modpack name.
- **Manage Backups**: List and restore previously backed up mods.
- **Mod Loader Selection**: Choose your mod loader to back up mods based on it.
- **Mod Pack Naming**: Organize backups by modpack name for each version and mod loader.

## Requirements

- Python 3.x
- `colorama` library

Install the required library using pip:

```bash
pip install colorama
