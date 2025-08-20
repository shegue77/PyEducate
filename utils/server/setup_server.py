from os.path import join, exists

from network.server.network import get_local_ip_address, validate_ip

from .paths import get_appdata_path
from .logger import log_error
from utils.crypto import encrypt_file, decrypt_file
from utils.server.admin import list_banned, ban_user, unban_user
from utils.server.help import show_version, show_license


def safe_mode(app_version, server_ip, server_port, ip_type, end_marker, command):
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

    print()
    command = str(command).strip().lower()

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
            ip_address = command.split()[1]
        except Exception as e:
            print("[!] IP address not specified!\n" "Unable to unban user!")
            log_error(e)
            return "[!] IP address not specified!\n" "Unable to unban user!"

        unban_user(ip_address)
    elif command.startswith("!version"):
        print(show_version(app_version))
    elif command.startswith("!license"):
        print(show_license())
    elif command.startswith("!showblacklist"):
        print(list_banned())
    elif command.startswith("!exit"):
        return "exit"

    elif command.startswith("!shutdown"):
        return "shutdown"
    else:
        print("[!] Invalid command!")


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
        if input("Change settings?: ").strip().lower() in ("y", "yes"):
            _change_settings(full_path)

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

    if input("Enter safe mode?: ").strip().lower() in ("y", "yes"):
        print()
        while True:
            command = input("Command: ")
            outcome = safe_mode(
                app_version, server_ip, server_port, ip_type, end_marker, command
            )
            if outcome == "exit" or outcome == "shutdown":
                break
    else:
        outcome = None

    return server_ip, server_port, ip_type, end_marker, outcome
