from os.path import join, exists

from utils.server.admin import safe_mode
from network.server.network import get_local_ip_address, validate_ip

from .paths import get_appdata_path
from .logger import log_error
from utils.crypto import encrypt_file, decrypt_file


def _change_settings(data_path: str):
    server_port = int(input("Enter server port: "))
    ip_type = str(input("Enter IP type (IPv4/IPv6): ")).lower()
    server_ip = str(input("Override your IP address (press the 'enter' key to skip): "))

    if ip_type.strip().lower() == "ipv6":
        if server_ip.strip().lower() != "":
            server_ip = get_local_ip_address(ip_type)
    else:
        if not validate_ip(server_ip):
            print(
                "\n[!] Invalid IPv4 address.\n" "Defaulting to automatic IP address.\n"
            )
            server_ip = get_local_ip_address(ip_type)

    with open(join(data_path, "connect-data.txt"), "wb") as f:
        f.write(encrypt_file(f"{server_port}\n{ip_type}\n{server_ip}"))

    return server_ip, server_port, ip_type


def setup(app_version, end_marker):
    full_path = get_appdata_path()
    if exists(join(full_path, "connect-data.txt")):

        answer = (
            str(input("Would you like to change any settings (y/n): ")).strip().lower()
        )

        if answer in ("y", "yes"):
            server_ip, server_port, ip_type = _change_settings(full_path)

        else:
            with open(join(full_path, "connect-data.txt"), "rb") as f:
                data = decrypt_file(f.read()).strip().splitlines()
                server_port = data[0]
                ip_type = data[1]
                try:
                    server_ip = data[2]
                except IndexError as ie:
                    log_error(ie)
                    server_ip = get_local_ip_address(ip_type)

    else:
        print("[!] Unable to locate save data!\n")
        server_ip, server_port, ip_type = _change_settings(full_path)

    emergency_command_prompt = str(
        input("Would you like to enter safe mode (DEBUG) (y/n): ").strip().lower()
    )
    if emergency_command_prompt in ("y", "yes"):
        print()
        outcome = safe_mode(app_version, server_ip, server_port, ip_type, end_marker)
    else:
        outcome = None

    return server_ip, server_port, ip_type, end_marker, outcome
