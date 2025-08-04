from datetime import datetime
from threading import Lock
from os.path import join
from json import load, loads, dump, JSONDecodeError
from .logger import log_error
from .paths import get_appdata_path

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
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = load(f)
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
        with open(file_path, "w", encoding="utf-8") as f:
            dump(json_data, f, indent=2)

    print(
        f"{ip_address} has been banned!\n"
        f"Run !disconnect to cut all"
        f" connections with {ip_address}."
    )


def unban_user(ip_address):
    file_path = str(join(get_appdata_path(), "banned-users.json"))

    try:
        with _safe_banned_users:
            with open(file_path, "r", encoding="utf-8") as f:
                data = load(f)

    except FileNotFoundError as fe:
        print("[*] Ban list not found.")
        with _safe_banned_users:
            with open(file_path, "w", encoding="utf-8") as f:
                json_data = {"banned_ips": {}}
                dump(json_data, f)

        log_error(fe)
        return

    except JSONDecodeError as je:
        with _safe_banned_users:
            with open(file_path, "w", encoding="utf-8") as f:
                json_data = {"banned_ips": {}}
                dump(json_data, f)
        log_error(je)
        return

    if ip_address in data["banned_ips"]:
        del data["banned_ips"][ip_address]

        with _safe_banned_users:
            with open(file_path, "w", encoding="utf-8") as f:
                dump(data, f, indent=2)

        print(f"[*] Unbanned {ip_address}")
    else:
        print(f"[!] IP address {ip_address} not found in ban list.")


def check_if_banned(ip_address):
    file_path = str(join(get_appdata_path(), "banned-users.json"))

    try:
        with _safe_banned_users:
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = load(f)

    except FileNotFoundError:
        print("[*] Ban list not found.")
        with _safe_banned_users:
            with open(file_path, "w", encoding="utf-8") as f:
                json_data = {"banned_ips": {}}
                dump(json_data, f)
        return False

    except JSONDecodeError:
        with _safe_banned_users:
            with open(file_path, "w", encoding="utf-8") as f:
                json_data = {"banned_ips": {}}
                dump(json_data, f)
        return False

    return bool(ip_address in json_data["banned_ips"].keys())


def list_banned():
    file_path = str(join(get_appdata_path(), "banned-users.json"))
    banned_ip_data = "\nBanned IP addresses:\n\n"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json_data = load(f)
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
