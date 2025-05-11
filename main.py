import os
import shutil
import re
from collections import Counter
from colorama import init, Fore, Style

init()

BASE_DIR = os.getcwd()
MODS_DIR = os.path.join(BASE_DIR, "mods")
BACKUPS_DIR = os.path.join(BASE_DIR, "mods_backups")

os.makedirs(BACKUPS_DIR, exist_ok=True)

def get_mod_files(folder):
    return sorted([
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f)) and f.endswith(".jar")
    ])

def detect_loader_and_version(folder):
    known_loaders = [
        "forge", "fabric", "neoforge", "quilt", "liteloader", "rift",
        "arclight", "canary", "magma", "mohist", "sponge", "vanilla"
    ]
    version_pattern = re.compile(r"(1\.\d+(\.\d+)?)")

    loader_hits = []
    version_hits = []

    for filename in get_mod_files(folder):
        lower = filename.lower()
        for loader in known_loaders:
            if f"-{loader}" in lower or f"_{loader}" in lower:
                loader_hits.append(loader)
        version_match = version_pattern.search(lower)
        if version_match:
            version_hits.append(version_match.group(1))

    loader = Counter(loader_hits).most_common(1)
    version = Counter(version_hits).most_common(1)

    return (
        loader[0][0] if loader else "unknown",
        version[0][0] if version else "unknown"
    )

def is_backup_matching(current_mods, backup_folder):
    backup_mods = get_mod_files(backup_folder)
    return current_mods == sorted(backup_mods)

def check_backup_status():
    if not os.listdir(MODS_DIR):
        print(f"{Fore.YELLOW}[!] 'mods' folder is empty, skipping check.{Style.RESET_ALL}")
        return True

    mods_now = get_mod_files(MODS_DIR)
    detected_loader, detected_version = detect_loader_and_version(MODS_DIR)

    backups = [
        b for b in os.listdir(BACKUPS_DIR)
        if os.path.isdir(os.path.join(BACKUPS_DIR, b))
    ]

    for backup in backups:
        path = os.path.join(BACKUPS_DIR, backup)
        if is_backup_matching(mods_now, path):
            print(f"{Fore.GREEN}[*] Mods are already backed up as '{backup}'.{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}[!] Detected loader: {detected_loader}, version: {detected_version}{Style.RESET_ALL}")
            return True

    best_match = None
    best_overlap = 0
    for backup in backups:
        path = os.path.join(BACKUPS_DIR, backup)
        backup_mods = get_mod_files(path)

        # check for partial match
        common = set(mods_now) & set(backup_mods)
        overlap_ratio = len(common) / max(len(mods_now), len(backup_mods))
        if overlap_ratio > best_overlap:
            best_overlap = overlap_ratio
            best_match = (backup, backup_mods, list(common))

    if best_overlap >= 0.6 and best_match:
        backup_name, backup_mods, common_mods = best_match
        added = list(set(mods_now) - set(backup_mods))
        removed = list(set(backup_mods) - set(mods_now))

        print(f"{Fore.YELLOW}[~] Mods are not exactly backed up, but similar to '{backup_name}' ({int(best_overlap*100)}% match).{Style.RESET_ALL}")
        if added:
            print(f"{Fore.CYAN}[+] New mods not in backup:{Style.RESET_ALL}")
            for m in added:
                print(f"    - {m}")
        if removed:
            print(f"{Fore.CYAN}[-] Missing mods that existed in backup:{Style.RESET_ALL}")
            for m in removed:
                print(f"    - {m}")

        update_backup = input(f"{Fore.YELLOW}[?] Do you want to update the backup '{backup_name}' with these changes? (y/n): {Style.RESET_ALL}").strip().lower()
        if update_backup == 'y':
            backup_mods(backup_name, mods_now)
            print(f"{Fore.GREEN}[*] Backup updated successfully.{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}[~] Skipping backup update.{Style.RESET_ALL}")
        
        # Regardless of the choice, print loader and version
        print(f"{Fore.MAGENTA}[!] Detected loader: {detected_loader}, version: {detected_version}{Style.RESET_ALL}")
        return False

    print(f"{Fore.RED}[x] These mods are not backed up.{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}[!] Detected loader: {detected_loader}, version: {detected_version}{Style.RESET_ALL}")
    return False

def clear_folder(folder):
    for item in os.listdir(folder):
        path = os.path.join(folder, item)
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

def backup_mods(backup_name=None, mods=None):
    if not backup_name or not mods:
        loader, version = detect_loader_and_version(MODS_DIR)
        modpack_name = input(f"{Fore.YELLOW}Enter a modpack name: {Style.RESET_ALL}").strip()
        if not modpack_name:
            print(f"{Fore.RED}[x] Modpack name cannot be empty.{Style.RESET_ALL}")
            return

        backup_name = f"{modpack_name}-{loader}-{version}"

    backup_path = os.path.join(BACKUPS_DIR, backup_name)

    if os.path.exists(backup_path):
        print(f"{Fore.YELLOW}[!] Backup '{backup_name}' already exists. Skipping.{Style.RESET_ALL}")
        return

    os.makedirs(backup_path)
    for f in os.listdir(MODS_DIR):
        s = os.path.join(MODS_DIR, f)
        d = os.path.join(backup_path, f)
        shutil.copy2(s, d)
    print(f"{Fore.GREEN}[*] Backup created: '{backup_name}'{Style.RESET_ALL}")

def list_backups():
    print(f"\n{Fore.BLUE}[+]{Style.RESET_ALL} Available backups:")
    backups = []
    for folder in os.listdir(BACKUPS_DIR):
        if os.path.isdir(os.path.join(BACKUPS_DIR, folder)):
            backups.append(folder)
    for i, b in enumerate(backups):
        print(f"  {i+1}. {b}")
    return backups

def move_to_mods(src_folder):
    clear_folder(MODS_DIR)
    for item in os.listdir(src_folder):
        s = os.path.join(src_folder, item)
        d = os.path.join(MODS_DIR, item)
        shutil.copy2(s, d)
    print(f"{Fore.GREEN}[*] Activated mods from '{src_folder}'{Style.RESET_ALL}")

def main():
    print(f"{Style.BRIGHT}=== Mod Folder Manager ==={Style.RESET_ALL}")

    mods_exist = bool(os.listdir(MODS_DIR))
    already_backed_up = check_backup_status() if mods_exist else True

    if mods_exist and not already_backed_up:
        backup_mods()
        clear_folder(MODS_DIR)
        print(f"{Fore.CYAN}[+] Cleared 'mods' folder after backup.{Style.RESET_ALL}")
    elif mods_exist and already_backed_up:
        print(f"{Fore.BLUE}[+] Mods were already backed up. Clearing 'mods' folder...{Style.RESET_ALL}")
        clear_folder(MODS_DIR)

    backups = list_backups()
    if not backups:
        print(f"{Fore.RED}[x] No backups found. Nothing to activate.{Style.RESET_ALL}")
        return

    choice = input(f"{Fore.YELLOW}[?] Which backup do you want to activate? (enter number): {Style.RESET_ALL}").strip()
    try:
        selected = backups[int(choice) - 1]
        move_to_mods(os.path.join(BACKUPS_DIR, selected))
    except:
        print(f"{Fore.RED}[x] Invalid selection.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
