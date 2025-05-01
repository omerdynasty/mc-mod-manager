import os
import shutil
from colorama import init, Fore, Style

init()

BASE_DIR = os.getcwd()
MODS_DIR = os.path.join(BASE_DIR, "mods")
BACKUPS_DIR = os.path.join(BASE_DIR, "mods_backups")

os.makedirs(BACKUPS_DIR, exist_ok=True)

def get_mod_files(folder):
    return sorted([
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ])

def is_backup_matching(mods_now, backup_folder):
    backup_mods = get_mod_files(backup_folder)
    return mods_now == sorted(backup_mods)

def check_if_current_mods_are_backed_up():
    if not os.listdir(MODS_DIR):
        print(f"{Fore.YELLOW}[!] 'mods' folder is empty, skipping backup check.{Style.RESET_ALL}")
        return True

    mods_now = get_mod_files(MODS_DIR)
    backups = [
        b for b in os.listdir(BACKUPS_DIR)
        if os.path.isdir(os.path.join(BACKUPS_DIR, b))
    ]

    for backup in backups:
        path = os.path.join(BACKUPS_DIR, backup)
        if is_backup_matching(mods_now, path):
            print(f"{Fore.GREEN}[*] Mods already backed up as '{backup}'{Style.RESET_ALL}")
            return True

    print(f"{Fore.RED}[x] Current mods are not backed up!{Style.RESET_ALL}")
    return False

def ask_for_loader():
    loaders = [
        "forge", "fabric", "neoforge", "quilt", "liteloader", "rift",
        "arclight", "canary", "magma", "mohist", "sponge", "vanilla"
    ]

    print(f"\n{Style.BRIGHT + Fore.CYAN}[?]{Style.RESET_ALL} Select your mod loader:")
    for i, loader in enumerate(loaders, start=1):
        print(f"  {i}. {loader}")

    choice = input(f"{Fore.YELLOW}Choose (1-{len(loaders)}): {Style.RESET_ALL}").strip()
    try:
        return loaders[int(choice)-1]
    except (ValueError, IndexError):
        return None

def ask_for_version():
    return input(f"{Fore.YELLOW}Enter Minecraft version (e.g. 1.21.4): {Style.RESET_ALL}").strip()

def ask_for_modpack_name():
    return input(f"{Fore.YELLOW}Enter modpack name: {Style.RESET_ALL}").strip()

def clear_folder(folder):
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        else:
            shutil.rmtree(item_path)

def backup_current_mods(loader, version, modpack_name):
    backup_name = f"{modpack_name}-{loader}-{version}"
    backup_path = os.path.join(BACKUPS_DIR, backup_name)

    if os.path.exists(backup_path):
        print(f"{Fore.YELLOW}[!] Backup '{backup_name}' already exists. Skipping backup.{Style.RESET_ALL}")
        return

    os.makedirs(backup_path)
    for item in os.listdir(MODS_DIR):
        s = os.path.join(MODS_DIR, item)
        d = os.path.join(backup_path, item)
        shutil.copy2(s, d) if os.path.isfile(s) else shutil.copytree(s, d)

    print(f"{Fore.GREEN}[*] Mods backed up as '{backup_name}'{Style.RESET_ALL}")

def list_existing_backups():
    print(f"\n{Style.BRIGHT + Fore.BLUE}[+]{Style.RESET_ALL} Available backups:")
    backups = []
    for folder in os.listdir(BACKUPS_DIR):
        path = os.path.join(BACKUPS_DIR, folder)
        if os.path.isdir(path):
            backups.append(folder)
    for i, b in enumerate(backups):
        print(f"  {i+1}. {b}")
    return backups

def move_to_mods(source_folder):
    clear_folder(MODS_DIR)
    for item in os.listdir(source_folder):
        s = os.path.join(source_folder, item)
        d = os.path.join(MODS_DIR, item)
        shutil.copy2(s, d) if os.path.isfile(s) else shutil.copytree(s, d)
    print(f"{Fore.GREEN}[*] Activated mods from '{source_folder}'{Style.RESET_ALL}")

def main():
    print(f"{Style.BRIGHT}=== Mod Folder Manager ==={Style.RESET_ALL}")

    mods_exist = bool(os.listdir(MODS_DIR))
    already_backed_up = check_if_current_mods_are_backed_up() if mods_exist else True

    if mods_exist and not already_backed_up:
        loader = ask_for_loader()
        version = ask_for_version()
        modpack_name = ask_for_modpack_name()

        if loader and version and modpack_name:
            backup_current_mods(loader, version, modpack_name)
            clear_folder(MODS_DIR)
            print(f"{Fore.CYAN}[+] Cleared 'mods' folder after backup.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[x] Invalid input. Aborting...{Style.RESET_ALL}")
            return
    elif mods_exist and already_backed_up:
        print(f"{Fore.BLUE}[+] Mods were already backed up. Clearing mods folder...{Style.RESET_ALL}")
        clear_folder(MODS_DIR)

    backups = list_existing_backups()
    if not backups:
        print(f"{Fore.RED}[x] No backups found. Nothing to activate.{Style.RESET_ALL}")
        return

    choice = input(f"\n{Fore.YELLOW}[?] Which one do you want to activate? (enter number): {Style.RESET_ALL}").strip()
    try:
        index = int(choice) - 1
        selected = backups[index]
        source_path = os.path.join(BACKUPS_DIR, selected)
        move_to_mods(source_path)
    except:
        print(f"{Fore.RED}[x] Invalid selection.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
