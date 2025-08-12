from datetime import datetime
from threading import Lock
from os.path import join
from json import loads, dumps, JSONDecodeError
from .logger import log_error
from .paths import get_appdata_path
from .help import show_version, show_license
from utils.crypto import decrypt_file, encrypt_file

_safe_banned_users = Lock()


def ban_user(command):
    try:
        ip_address = command.split(" ")[1]
    except IndexError:
        print("[!] IP address not specified!\nUnable to ban user!")
        return None
    try:
        reason = command.split(" ")[2]
    except Exception:
        reason = "Unknown"
    try:
        severity = command.split(" ")[3]
    except Exception:
        severity = "Unknown"
    try:
        end_date = command.split(" ")[4]
    except Exception:
        end_date = "Indefinite"

    file_path = str(join(get_appdata_path(), "banned-users.json"))
    try:
        with _safe_banned_users:
            with open(file_path, "rb") as f:
                json_data = loads(decrypt_file(f.read()))

    except FileNotFoundError:
        json_data = {"banned_ips": {}}
    except JSONDecodeError:
        json_data = {"banned_ips": {}}

    if reason.strip() == "":
        reason = "Unknown"
    if end_date.strip() == "":
        end_date = "Indefinite"
    if severity.strip() == "":
        severity = "Unknown"

    now = datetime.now()
    timestamp = now.strftime("%d-%m-%Y%H:%M:%S")
    new_ban = loads(
        '{"timestamp": '
        + f'"{timestamp}", '
        + f'"reason": "{reason}", '
        + f'"severity": "{severity}", '
        + f'"end_date": "{end_date}"'
        + "}"
    )

    json_data["banned_ips"][ip_address] = new_ban

    with _safe_banned_users:
        with open(file_path, "wb") as file:
            json_data = dumps(json_data)
            file.write(encrypt_file(json_data))

    print(
        f"{ip_address} has been banned!\n"
        f"Run !disconnect to cut all"
        f" connections with {ip_address}."
    )


def unban_user(ip_address):
    file_path = str(join(get_appdata_path(), "banned-users.json"))

    try:
        with _safe_banned_users:
            with open(file_path, "rb") as f:
                data = loads(decrypt_file(f.read()))

    except FileNotFoundError as fe:
        print("[*] Ban list not found.")
        with _safe_banned_users:
            with open(file_path, "wb") as file:
                json_data = {"banned_ips": {}}
                json_data = dumps(json_data)
                file.write(encrypt_file(json_data))

        log_error(fe)
        return

    except JSONDecodeError as je:
        with _safe_banned_users:
            with open(file_path, "wb") as file:
                json_data = {"banned_ips": {}}
                json_data = dumps(json_data)
                file.write(encrypt_file(json_data))
        log_error(je)
        return

    if ip_address in data["banned_ips"]:
        del data["banned_ips"][ip_address]

        with _safe_banned_users:
            with open(file_path, "wb") as file:
                data = dumps(data)
                file.write(encrypt_file(data))

        print(f"[*] Unbanned {ip_address}")
    else:
        print(f"[!] IP address {ip_address} not found in ban list.")


def check_if_banned(ip_address):
    file_path = str(join(get_appdata_path(), "banned-users.json"))

    try:
        with _safe_banned_users:
            with open(file_path, "rb") as f:
                json_data = loads(decrypt_file(f.read()))

    except FileNotFoundError:
        print("[*] Ban list not found.")
        with _safe_banned_users:
            with open(file_path, "wb") as file:
                json_data = {"banned_ips": {}}
                json_data = dumps(json_data)
                file.write(encrypt_file(json_data))
        return False

    except JSONDecodeError:
        with _safe_banned_users:
            with open(file_path, "wb") as file:
                json_data = {"banned_ips": {}}
                json_data = dumps(json_data)
                file.write(encrypt_file(json_data))
        return False

    return bool(ip_address in json_data["banned_ips"].keys())


def list_banned():
    file_path = str(join(get_appdata_path(), "banned-users.json"))
    banned_ip_data = "\nBanned IP addresses:\n\n"

    try:
        with open(file_path, "rb") as f:
            json_data = loads(decrypt_file(f.read()))

    except FileNotFoundError:
        json_data = {"banned_ips": {}}
    except JSONDecodeError:
        json_data = {"banned_ips": {}}

    for part in json_data["banned_ips"]:
        banned_ip_data += f"IP: " f"{part}:\n"
        banned_ip_data += f"Reason: " f'{json_data["banned_ips"][part]["reason"]}\n'
        banned_ip_data += f"Severity: " f'{json_data["banned_ips"][part]["severity"]}\n'
        banned_ip_data += (
            f"Timestamp: " f'{json_data["banned_ips"][part]["timestamp"]}\n\n'
        )

    return banned_ip_data


def safe_mode(app_version, server_ip, server_port, ip_type, end_marker):
    print("Emergency Console | Safe Boot")
    print("Server Status: Offline")
    print("\nExit safe mode to start the server.\n\n")
    safe_mode_commands = """
Emergency Commands:
!help
    Shows the available commands.

!info
    Displays info about the server.

!version
    Shows the version of the application.

!license
    Shows license information about the application.

!showblacklist
    Displays the list of all banned IP addresses.

!ban <IP_ADDRESS> [reason] [severity]
    Bans an IP address from connecting to the server.
    Example: !ban 127.0.0.1 port_scanning high

!unban <IP_ADDRESS>
    Removes the ban from the specified IP address.
    Example: !unban 127.0.0.1

!exit
    Exits safe mode.

!shutdown
    Kills the program.
    """
    print(safe_mode_commands)

    while True:
        print()
        command = str(input("Command: ")).strip().lower()

        if command.startswith("!help"):
            print(safe_mode_commands)

        elif command.startswith("!info"):
            print(
                f"SERVER IP: {server_ip}\n"
                f"SERVER PORT: {server_port}\n"
                f"IP TYPE: {ip_type}\n"
                f"End marker: {end_marker.decode()}\n"
            )
        elif command.startswith("!ban"):
            ban_user(command)
        elif command.startswith("!unban"):
            try:
                ip_address = str(command).strip().lower().split()[1]
            except Exception as e:
                print("[!] IP address not specified!\n" "Unable to unban user!")
                log_error(e)
                continue

            unban_user(ip_address)
        elif command.startswith("!version"):
            print(show_version(app_version))
        elif command.startswith("!license"):
            print(show_license())
        elif command.startswith("!showblacklist"):
            print(list_banned())
        elif command.startswith("!exit"):
            break

        elif command.startswith("!shutdown"):
            return "shutdown"
        else:
            print("[!] Invalid command!")
