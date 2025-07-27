# Copyright (C) 2025 shegue77
# SPDX-License-Identifier: GPL-3.0-or-later

# ---------------------------[ DEPENDENCIES ]---------------------------
import socket
from threading import Thread, Lock
from json import load, loads, dump, dumps, JSONDecodeError
from os import getenv, makedirs
from datetime import datetime
from os.path import exists as os_path_exists, expanduser, join
from platform import system
from sys import exit as sys_exit
from schedule import every, run_pending

# ----------------------------------------------------------------------


# -------------------------[ GLOBAL VARIABLES ]-------------------------
clients: dict = {}  # Keeps track of clients
usernames: dict = {}  # Keeps track of usernames of clients
active_threads: list = []  # Keeps track of (most) active threads.
END_MARKER = (
    b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"  # End marker used when sending JSON files,
)
# MAKE SURE this does NOT appear at all in your JSON file.
# MAKE SURE that this end marker MATCHES the end marker on the client.
safe_leaderboard = Lock()
safe_banned_users = Lock()
# ----------------------------------------------------------------------


# Gets the full path to APPDATA.
def get_appdata_path():
    user_os = system()
    if user_os == "Windows":
        path_to_appdata = getenv("APPDATA")
    elif user_os == "Darwin":
        path_to_appdata = expanduser("~/Library/Application Support")
    else:
        path_to_appdata = getenv("XDG_DATA_HOME", expanduser("~/.local/share"))

    if os_path_exists(join(path_to_appdata, "PyEducate")):
        if os_path_exists((join(path_to_appdata, "PyEducate", "server"))):
            full_path_data = join(path_to_appdata, "PyEducate", "server")
        else:
            full_path_data = join(path_to_appdata, "PyEducate", "server")
            makedirs(full_path_data)
    else:
        makedirs(join(path_to_appdata, "PyEducate"))
        makedirs(join(path_to_appdata, "PyEducate", "server"))
        full_path_data = join(path_to_appdata, "PyEducate", "server")

    return full_path_data


def log_error(data):

    # Get current time
    now = datetime.now()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    log_path = str(join(get_appdata_path(), "server.log"))

    data = str(timestamp + " " + str(data) + "\n")

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(data)

    except FileNotFoundError:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(data)

    except PermissionError:
        print(f"[!] Insufficient permissions!\n" f"Unable to log data at {log_path}!")


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
        with safe_banned_users:
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

    with safe_banned_users:
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
        with safe_banned_users:
            with open(file_path, "r", encoding="utf-8") as f:
                data = load(f)

    except FileNotFoundError:
        print("Ban list not found.")
        with safe_banned_users:
            with open(file_path, "w", encoding="utf-8") as f:
                json_data = {"banned_ips": {}}
                dump(json_data, f)
        return

    except JSONDecodeError:
        with safe_banned_users:
            with open(file_path, "w", encoding="utf-8") as f:
                json_data = {"banned_ips": {}}
                dump(json_data, f)
        return

    if ip_address in data["banned_ips"]:
        del data["banned_ips"][ip_address]

        with safe_banned_users:
            with open(file_path, "w", encoding="utf-8") as f:
                dump(data, f, indent=2)

        print(f"Unbanned {ip_address}")
    else:
        print(f"IP address {ip_address} not found in ban list.")


def check_if_banned(ip_address):
    file_path = str(join(get_appdata_path(), "banned-users.json"))

    try:
        with safe_banned_users:
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = load(f)

    except FileNotFoundError:
        print("Ban list not found.")
        with safe_banned_users:
            with open(file_path, "w", encoding="utf-8") as f:
                json_data = {"banned_ips": {}}
                dump(json_data, f)
        return False

    except JSONDecodeError:
        with safe_banned_users:
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


# Parses and sends the JSON file to the client.
def send_json(client, file_path, id_n=None):

    try:
        file = open(file_path, "r", encoding="utf-8")
    except FileNotFoundError:
        file_path = str(join(get_appdata_path(), "lessons.json"))
        file = open(file_path, "r", encoding="utf-8")

    full_data = file.read()

    try:
        loads(full_data)
    except Exception as e:
        print("[!] INVALID JSON! Sending failed!")
        print(e)
        log_error(e)
        return

    data = loads(full_data)

    if id_n is None:
        sending_data = dumps(data.get("lessons", []))

    else:
        id_n = list(id_n)
        sending_data = []

        for id_s in id_n:
            id_found = False
            for lesson in data["lessons"]:
                if int(lesson["id"]) == int(id_s):
                    sending_data.append(lesson)
                    id_found = True
                    break

            if not id_found:
                print(f"ID {id_s} not found in {file_path}!")

        sending_data = dumps(sending_data)

    client.sendall(sending_data.encode())

    if END_MARKER in sending_data.encode():
        print(
            f"[!] END MARKER FOUND IN {file_path}, "
            f"SENDING POTENTIALLY CORRUPTED DATA."
        )

    client.sendall(bytes(END_MARKER))

    file.close()


def send_leaderboard(client, filename):

    try:
        file = open(filename, "r", encoding="utf-8")
    except FileNotFoundError:
        filename = str(join(get_appdata_path(), "leaderboards.json"))
        file = open(filename, "w", encoding="utf-8")

    file.close()
    full_data = str(clean_leaderboard(filename))

    try:
        loads(full_data)
    except Exception as e:
        print("[!] INVALID JSON! Sending failed!")
        print(e)
        log_error(e)
        return

    data = loads(full_data)
    data = dumps(data)

    client.sendall(data.encode())

    if END_MARKER in data.encode():
        print(
            f"[!] END MARKER FOUND IN {filename},"
            f" SENDING POTENTIALLY CORRUPTED DATA."
        )

    client.sendall(bytes(END_MARKER))


# Load the leaderboard from the JSON file
def read_leaderboard(filename):
    with safe_leaderboard:
        if not os_path_exists(filename):
            # Create empty file if it doesn't exist
            with open(filename, "w", encoding="utf-8") as f:
                dump([], f)
            return []

        with open(filename, "r", encoding="utf-8") as f:
            return load(f)


def clean_leaderboard(file_path):
    def get_top_n_users(filename, n=10, type_n="points"):
        leaderboard = read_leaderboard(filename)
        # Sort by points descending
        sorted_leaderboard = sorted(leaderboard, key=lambda x: x[type_n], reverse=True)
        return sorted_leaderboard[:n]

    def get_board_types(file_path):

        def create_json():
            with open(file_path, "w", encoding="utf-8") as file:
                json_data = []
                dump(json_data, file, indent=4)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = load(f)

        except FileNotFoundError as fe:
            log_error(fe)
            create_json()

        except JSONDecodeError:
            with open(file_path, "w", encoding="utf-8") as file:
                data = []
                dump(data, file)

        leaderboard_items = []

        for part in data:
            for i in part.keys():
                if i != "username":
                    leaderboard_items.append(i)
            break

        return leaderboard_items

    file_data_types = get_board_types(file_path)
    file_data = []
    for part in file_data_types:
        board_items = get_top_n_users(file_path, 10, str(part))
        for person in board_items:
            found = False
            for file_part in file_data:
                if person["username"] == file_part["username"]:
                    found = True
                    break

            if not found:
                file_data.append(person)

    print(dumps(file_data))
    return dumps(file_data)


def update_leaderboard(username, point_amount, lesson_completed):
    file_name = str(join(get_appdata_path(), "leaderboards.json"))

    # Save the leaderboard to the JSON file
    def write_leaderboard(filename, leaderboard):
        with safe_leaderboard:
            with open(filename, "w", encoding="utf-8") as f:
                dump(leaderboard, f, indent=4)

    # Add or update a user in the leaderboard
    def add_or_update_user(filename, user, points, lessons_completed):
        leaderboard = read_leaderboard(filename)
        found = False

        for entry in leaderboard:
            if entry["username"] == user:
                entry["points"] = points
                entry["lessons_completed"] = lessons_completed
                found = True
                break

        if not found:
            leaderboard.append(
                {
                    "username": user,
                    "points": points,
                    "lessons_completed": lessons_completed,
                }
            )

        write_leaderboard(filename, leaderboard)

    if username == "Unknown":
        return None

    add_or_update_user(file_name, username, point_amount, lesson_completed)


# Function to handle each connected client
def handle_client(client_socket, addr):
    if check_if_banned(addr):
        client_socket.sendall("!disconnect".encode())
        client_socket.close()
        clients.pop(addr, None)
        usernames.pop(addr, None)
        return None

    clients[addr] = client_socket

    print(f"[!] {addr[0]} connected.")

    try:
        client_socket.sendall("!getusername".encode())
    except Exception as er:
        log_error(er)

    while True:
        try:
            response = client_socket.recv(4096).decode().strip().lower()
            if not response:
                break

            if str(response).startswith("!getusername"):
                username = response.split(" ")[1].strip()
                usernames[addr] = username

            elif str(response).startswith("!getstats"):
                points = int(response.split(" ")[1])
                lessons_completed = int(response.split(" ")[2])
                username = usernames.get(addr, "Unknown")

                update_leaderboard(username, points, lessons_completed)

            else:
                print(f"\n[{addr[0]} Output]: {response}")

        except (ConnectionResetError, BrokenPipeError):
            break

    print(f"[!] Client {addr[0]} disconnected.")
    client_socket.close()
    del clients[addr]
    usernames.pop(addr, None)


# Function is used to safely shutdown the server.
# Is run when !shutdown is called.
def disconnect(clients_list, server_m):
    global active_threads

    if any(t.is_alive() for t in active_threads):
        print(
            "[!] Potentially active threads detected. "
            "Please make sure all threads are "
            "closed to prevent critical data loss.\n"
            "(Note that this may be a false positive "
            "but please proceed with caution)\n"
        )

        if (
            str(
                input(
                    "[*] Would you like to continue the server shutdown - "
                    "NOT RECOMMENDED (y/n): "
                )
            )
            == "y"
        ):
            print("[!!] Proceeding with potentially " "unsafe server shutdown...\n")

        else:
            print("Server shutdown safely aborted.\n")
            return

    else:
        if (
            str(
                input(
                    "[*] No active threads detected. "
                    "Would you like to continue the server shutdown (y/n): "
                )
            )
            .strip()
            .lower()
            == "y"
        ):
            print("\n[*] Shutting down server...")

        else:
            print("[*] Server shutdown safely aborted.\n")
            return

    active_threads = [t for t in active_threads if t.is_alive()]

    for client in clients_list:
        client.sendall("!disconnect".encode())
        client.close()

    server_m.close()
    sys_exit(0)


def show_license():
    data = """
PyEducate Server - Server application used to send data such as lessons to clients.
Copyright (C) 2025 shegue77

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
    return data


def show_version():
    data = """
PyEducate Server v1.0.0-rc0 | Copyright (C) 2025 shegue77
This program comes with ABSOLUTELY NO WARRANTY.
This software is released under the GNU GPL; run !license for details.
"""
    return data


# Displays help data for commands.
def help_data():
    data = """

Available Commands:

    !help
        Opens the help list.

    !info
        Shows information of the server.

    !version
        Shows the version of the application.

    !license
        Shows the license of the application.

    !getip
        Gets the public IPv4 address of client(s).

    !gethostname
        Gets the hostname of client(s).

    !getusername
        Gets the username of client(s).

    !getstats
        Gets leaderboard data of client(s), used to update their leaderboard.

    !updateboard [path]
        Parses and sends leaderboard data of the top 10 which is in a leaderboard JSON to client(s).
        Example: !updateboard leaderboards.json

    !sendlesson <lesson_ID> [path]
        Sends specific lesson(s) from a JSON file containing lessons (identified by ID) to client(s).
        Example 1: !sendlesson [2] lessons.json
        Example 2: !sendlesson [1, 3, 4] lessons.json

    !sendjson [path]
        Sends a JSON file containing ALL lessons to client(s).
        Example: !sendjson lessons.json

    !showblacklist
        Displays the list of all banned IP addresses.

    !ban <IP_ADDRESS> [reason] [severity]
        Bans (prevents) an IP address from connecting to the server.
        Example: !ban 127.0.0.1 port_scanning high

    !unban <IP_ADDRESS>
        Removes the ban from the specified IP address.
        Example: !unban 127.0.0.1

    !disconnect
        Cuts a connection with client(s).

    !shutdown
        Safely disconnects all clients before shutting down the server.
        Use with caution.

Notes:
- Arguments in <> are required.
- Arguments in [] are optional.
- To refresh client list & command prompt, press the 'enter' key.

    """
    return data


# Starts the server and listens for clients.
def start_server(
    host, port, server_type="ipv4", marker_end=b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"
):

    if server_type == "ipv6":
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if str(host) == "" or str(host) == "::" or str(host) == "0.0.0.0":
        host = str(
            input(
                ""
                "[!!] Warning!"
                "A critical security risk has been found!\n"
                "Please enter your IP address (not '', 0.0.0.0 or ::): "
            )
        )
        if str(host) == "" or str(host) == "::" or str(host) == "0.0.0.0":
            print("Unable to start server due to security risks.\nShutting down...")
            return

    server.bind((host, port))
    server.listen()
    print(show_version())
    print("Press the 'enter' key to refresh client list " "& the command prompt.\n")
    print(
        "For more help about the commands of this application, "
        "run !help to view all commands with explanations.\n"
    )
    print(f"[*] Listening on {host}:{port}")

    # Start accepting client connections

    Thread(target=accept_clients, args=(server,), daemon=True).start()

    print("Waiting for clients to connect...")

    data = (host, port, server_type, marker_end)
    every(30).seconds.do(lambda: print("Waiting for clients to connect..."))
    process_commands(
        server, data
    )  # Start processing commands for the connected clients


# Function to accept incoming client connections
def accept_clients(server):
    while True:
        client_socket, addr = server.accept()
        Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()


# Function to process commands and communicate with the client
def process_commands(server, server_data):

    while True:
        if not clients:
            run_pending()
            continue

        print("\n[Connected Clients]")
        for idx, addr in enumerate(clients.keys(), start=1):
            username = usernames.get(addr, "Unknown")
            print(f"{idx}. {addr[0]} - {username}")

        choice = input("Select client number (or 0 to broadcast): ")

        try:
            choice = int(choice) - 1
        except ValueError:

            if str(choice).strip().lower().startswith("!help") or str(
                choice
            ).strip().lower().startswith("help"):
                print(help_data())
            elif str(choice).strip().lower().startswith("!info"):
                print(
                    f"SERVER IP: {server_data[0]}\n"
                    f"SERVER PORT: {server_data[1]}\n"
                    f"IP TYPE: {server_data[2]}\n"
                    f"End marker: {str(server_data[3])}\n"
                )
            elif str(choice).strip().lower().startswith("!ban"):
                ban_user(str(choice).strip().lower())
            elif str(choice).strip().lower().startswith("!unban"):
                try:
                    ip_address = str(choice).strip().lower().split()[1]
                except Exception:
                    print("[!] IP address not specified! " "Unable to unban user!")
                    continue
                unban_user(ip_address)

            elif str(choice).strip().lower().startswith("!version"):
                print(show_version())
            elif str(choice).strip().lower().startswith("!license"):
                print(show_license())
            elif str(choice).strip().lower().startswith("!showblacklist"):
                print(list_banned())
            elif str(choice).strip().lower().startswith("!shutdown"):
                disconnect(clients.values(), server)

            continue

        if choice == -1:
            # Broadcast command to all clients
            command = input("Enter command to send (broadcast): ").strip().lower()

            if command.startswith("!help") or command.startswith("help"):
                print(help_data())

            elif command.startswith("!shutdown"):
                disconnect(clients.values(), server)

            elif command.startswith("!info"):
                print(
                    f"SERVER IP: {server_data[0]}\n"
                    f"SERVER PORT: {server_data[1]}\n"
                    f"IP TYPE: {server_data[2]}\n"
                    f"End marker: {str(server_data[3])}\n"
                )

            elif command == "":
                continue

            elif command.startswith("!updateboard"):

                for client in clients.values():
                    try:
                        file_path_json = command.split(" ")[1]

                    except IndexError:
                        file_path_json = join(get_appdata_path(), "leaderboards.json")

                    except Exception as er:
                        file_path_json = join(get_appdata_path(), "leaderboards.json")
                        log_error(er)

                    client.sendall(str("!updateboard").encode())

                    thread = Thread(
                        target=send_leaderboard, args=(client, file_path_json)
                    )

                    thread.start()
                    active_threads.append(thread)

            elif command.startswith("!sendjson") or command.startswith("!sendlesson"):
                for client in clients.values():
                    if command.startswith("!sendjson"):
                        try:
                            file_path_json = command.split(" ")[1]

                        except IndexError:
                            file_path_json = join(get_appdata_path(), "lessons.json")

                        except Exception as er:
                            file_path_json = join(get_appdata_path(), "lessons.json")
                            log_error(er)

                    else:
                        try:
                            lesson_id = command.replace("]", "[").split("[")[1]
                            lesson_id = lesson_id.replace(",", "").split(" ")

                        except Exception as ie:
                            log_error(ie)
                            print("[!] LESSON ID NOT SPECIFIED!")
                            continue

                        try:
                            file_path_json = command.split("] ")[-1]

                        except IndexError:
                            file_path_json = join(get_appdata_path(), "lessons.json")

                        except Exception as er:
                            file_path_json = join(get_appdata_path(), "lessons.json")
                            log_error(er)

                    client.sendall(str("!sendjson").encode())

                    if command.startswith("!sendjson"):
                        thread = Thread(target=send_json, args=(client, file_path_json))
                    else:
                        thread = Thread(
                            target=send_json, args=(client, file_path_json, lesson_id)
                        )

                    thread.start()
                    active_threads.append(thread)

            elif command.startswith("!showblacklist"):
                print(list_banned())

            elif command.startswith("!version"):
                print(show_version())
            elif command.startswith("!license"):
                print(show_license())

            elif command.startswith("!ban"):
                ban_user(command)

            elif command.startswith("!unban"):
                try:
                    ip_address = str(choice).strip().lower().split()[1]
                except Exception:
                    print("[!] IP address not specified! " "Unable to unban user!")
                    continue

                unban_user(ip_address)

            else:
                for client in clients.values():
                    client.sendall(command.encode())

        elif 0 <= choice < len(clients):
            target_addr = list(clients.keys())[choice]
            command = (
                input(f"Enter command to send to {target_addr[0]}: ").strip().lower()
            )

            if command.startswith("!sendjson") or command.startswith("!sendlesson"):
                if command.startswith("!sendjson"):
                    try:
                        file_path_json = command.split(" ")[1]

                    except IndexError:
                        file_path_json = join(get_appdata_path(), "lessons.json")

                    except Exception as er:
                        file_path_json = join(get_appdata_path(), "lessons.json")
                        log_error(er)

                else:
                    try:
                        lesson_id = command.replace("]", "[").split("[")[1]
                        lesson_id = lesson_id.replace(",", "").split(" ")

                    except Exception as ie:
                        log_error(ie)
                        print("[!] LESSON ID NOT SPECIFIED!")
                        continue

                    try:
                        file_path_json = command.split("] ")[-1]

                    except IndexError:
                        file_path_json = join(get_appdata_path(), "lessons.json")

                    except Exception as er:
                        file_path_json = join(get_appdata_path(), "lessons.json")
                        log_error(er)

                clients[target_addr].sendall(str("!sendjson").encode())

                if command.startswith("!sendjson"):
                    thread = Thread(
                        target=send_json, args=(clients[target_addr], file_path_json)
                    )
                else:
                    thread = Thread(
                        target=send_json,
                        args=(clients[target_addr], file_path_json, lesson_id),
                    )

                thread.start()
                active_threads.append(thread)

            elif command.startswith("!updateboard"):
                try:
                    file_path_json = command.split(" ")[1]

                except IndexError:
                    file_path_json = join(get_appdata_path(), "leaderboards.json")

                except Exception as er:
                    file_path_json = join(get_appdata_path(), "leaderboards.json")
                    log_error(er)

                clients[target_addr].sendall(str("!updateboard").encode())

                thread = Thread(
                    target=send_leaderboard, args=(clients[target_addr], file_path_json)
                )

                thread.start()
                active_threads.append(thread)

            elif command == "":
                continue

            elif command.startswith("!help"):
                print(help_data())

            elif command.startswith("!info"):
                print(
                    f"SERVER IP: {server_data[0]}\n"
                    f"SERVER PORT: {server_data[1]}\n"
                    f"IP TYPE: {server_data[2]}\n"
                    f"End marker: {str(server_data[3])}\n"
                )

            elif command.startswith("!shutdown"):
                print(
                    "[!] Unsupported command,"
                    "please use broadcast to run !shutdown.\n"
                    "Did you mean !exit?"
                )

            elif command.startswith("!showblacklist"):
                print(list_banned())

            elif command.startswith("!ban"):
                ban_user(command)

            elif command.startswith("!unban"):
                try:
                    ip_address = str(choice).strip().lower().split()[1]
                except Exception:
                    print("[!] IP address not specified!" "Unable to unban user!")
                    continue

                unban_user(ip_address)

            else:
                clients[target_addr].sendall(command.encode())

        else:
            print("[!] Invalid selection.")


# Reads the data about the IP, PORT
# and IP TYPE (IPv4/IPv6) of the server
# and connects to the server.
if __name__ == "__main__":
    full_path = get_appdata_path()
    ANSWER = str(input("Would you like to change any settings (y/n): ")).strip().lower()
    if ANSWER in ("y", "yes"):
        SERVER_PORT = int(input("Enter server port: "))
        IP_TYPE = str(input("Enter IP type (IPv4/IPv6): ")).lower()

        SERVER_IP: str = ""
        if IP_TYPE.strip() == "ipv6":

            hostname = socket.gethostname()
            try:
                for info in socket.getaddrinfo(hostname, None):
                    if info[0] == socket.AF_INET6:  # Check for IPv6
                        SERVER_IP = str(info[4][0])

                if SERVER_IP == "":
                    SERVER_IP = input("Enter local IP address (IPv6): ")
            except socket.gaierror:

                SERVER_IP = input("Enter local IP address (IPv6): ")

        else:
            SERVER_IP = socket.gethostbyname(socket.gethostname())

        with open(join(full_path, "connect-data.txt"), "w", encoding="utf-8") as f:
            f.write(f"{SERVER_PORT}\n{IP_TYPE}")

        print(SERVER_IP)

    try:
        with open(join(full_path, "connect-data.txt"), "r", encoding="utf-8") as f:
            SERVER_PORT = int(f.readline().strip().replace(" ", ""))
            try:
                IP_TYPE = str(f.readline().strip()).lower()

            except Exception as e:
                print(
                    "[!] Unable to extract IP type (IPv4/IPv6)," "defaulting to IPv4..."
                )
                IP_TYPE = "ipv4"
                log_error(e)

            END_MARKER = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"

        if IP_TYPE.strip() == "ipv6":
            hostname = socket.gethostname()
            try:
                for info in socket.getaddrinfo(hostname, None):
                    if info[0] == socket.AF_INET6:  # Check for IPv6
                        SERVER_IP = str(info[4][0])

                if SERVER_IP == "":
                    SERVER_IP = input("Enter local IP address (IPv6): ")

            except socket.gaierror:
                print("Hostname could not be resolved.")
                SERVER_IP = input("Enter local IP address (IPv6): ")

        else:
            SERVER_IP = socket.gethostbyname(socket.gethostname())

    except FileNotFoundError as fe:
        log_error(fe)
        print("[!] Unable to locate save data!\n")
        SERVER_PORT = int(input("Enter server port: "))
        IP_TYPE = str(input("Enter IP type (IPv4/IPv6): ")).lower()
        END_MARKER = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"

        if IP_TYPE.strip() == "ipv6":
            hostname = socket.gethostname()
            try:
                for info in socket.getaddrinfo(hostname, None):
                    if info[0] == socket.AF_INET6:  # Check for IPv6
                        SERVER_IP = str(info[4][0])

                if SERVER_IP == "":
                    SERVER_IP = input("Enter local IP address (IPv6): ")

            except socket.gaierror:
                print("Hostname could not be resolved.")
                SERVER_IP = input("Enter local IP address (IPv6): ")

        else:
            SERVER_IP = socket.gethostbyname(socket.gethostname())

        with open(join(full_path, "connect-data.txt"), "w", encoding="utf-8") as f:
            f.write(f"{SERVER_PORT}\n{IP_TYPE}")

    EMERGENCY_COMMAND_PROMPT = str(
        input("Would you like to enter safe mode (DEBUG) (y/n): ")
    )
    if EMERGENCY_COMMAND_PROMPT in ("y", "yes"):
        print()
        print("Emergency Console | Safe Boot")
        print("Server Status: Offline")
        print("\nExit safe mode to start the server.\n\n")
        SAFE_MODE_COMMANDS = """
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
        Bans (prevents) an IP address from connecting to the server.
        Example: !ban 127.0.0.1 port_scanning high

    !unban <IP_ADDRESS>
        Removes the ban from the specified IP address.
        Example: !unban 127.0.0.1

    !exit
        Exits safe mode.

    !shutdown
        Kills the program.
"""
        print(SAFE_MODE_COMMANDS)

        while True:
            print()
            COMMAND = str(input("Command: ")).strip().lower()

            if COMMAND.startswith("!help"):
                print(SAFE_MODE_COMMANDS)
            elif COMMAND.startswith("!info"):
                print(
                    f"SERVER IP: {SERVER_IP}\n"
                    f"SERVER PORT: {SERVER_PORT}\n"
                    f"IP TYPE: {IP_TYPE}\n"
                    f"End marker: {END_MARKER.decode()}\n"
                )
            elif COMMAND.startswith("!ban"):
                ban_user(COMMAND)
            elif COMMAND.startswith("!unban"):
                try:
                    ip_address = str(COMMAND).strip().lower().split()[1]
                except Exception:
                    print("[!] IP address not specified!\n" "Unable to unban user!")
                    continue
                unban_user(ip_address)
            elif COMMAND.startswith("!version"):
                print(show_version())
            elif COMMAND.startswith("!license"):
                print(show_license())
            elif COMMAND.startswith("!showblacklist"):
                print(list_banned())
            elif COMMAND.startswith("!exit"):
                break
            elif COMMAND.startswith("!shutdown"):
                sys_exit(0)
            else:
                print("[!] Invalid command!")

    start_server(SERVER_IP, SERVER_PORT, IP_TYPE, END_MARKER)
