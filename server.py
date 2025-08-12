# Copyright (C) 2025 shegue77
# SPDX-License-Identifier: GPL-3.0-or-later

# ---------------------------[ DEPENDENCIES ]---------------------------
import socket
from threading import Thread
from os.path import join
from sys import exit as sys_exit
from schedule import every, run_pending

from utils.server.paths import get_appdata_path
from utils.server.logger import log_error
from utils.server.admin import ban_user, unban_user, check_if_banned, list_banned
from utils.server.help import show_version, show_license, help_data
from utils.server.storage import update_leaderboard
from network.server.storage import send_leaderboard, send_json
from utils.server.SetupServer import setup

# ----------------------------------------------------------------------


# -------------------------[ GLOBAL VARIABLES ]-------------------------
app_version = "v1.2.0"
clients: dict = {}  # Keeps track of clients
usernames: dict = {}  # Keeps track of usernames of clients
active_threads: list = []  # Keeps track of (most) active threads.
END_MARKER = (
    b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"
    # End marker used when sending JSON files.
    # MAKE SURE this does NOT appear at all in your JSON file.
    # MAKE SURE that this end marker MATCHES the end marker on the client.
)
# ----------------------------------------------------------------------


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
                points = float(response.split(" ")[1])
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
            print("[*] Server shutdown safely aborted.\n")
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
                "\n"
                "[!!] Warning! "
                "A security risk has been found!\n"
                "Please verify that you want to bind to all network interfaces.\n"
                "Please enter your IP address (not the following "
                "unless you want to bind to all network "
                "interfaces -> ('', 0.0.0.0 or :: ): "
            )
        )
        if str(host) == "" or str(host) == "::" or str(host) == "0.0.0.0":
            print("[*] Binding to all network interfaces.")

    server.bind((host, port))
    server.listen()
    print(show_version(app_version))
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
                    "\n"
                    f"SERVER IP: {server_data[0]}\n"
                    f"SERVER PORT: {server_data[1]}\n"
                    f"IP TYPE: {server_data[2]}\n"
                    f"End marker: {str(server_data[3])}\n"
                    f"Log file: {str(join(get_appdata_path(), 'server.log'))}"
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
                print(show_version(app_version))
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
                        target=send_leaderboard,
                        args=(client, file_path_json, END_MARKER),
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
                        thread = Thread(
                            target=send_json, args=(client, file_path_json, END_MARKER)
                        )
                    else:
                        thread = Thread(
                            target=send_json,
                            args=(client, file_path_json, END_MARKER, lesson_id),
                        )

                    thread.start()
                    active_threads.append(thread)

            elif command.startswith("!showblacklist"):
                print(list_banned())

            elif command.startswith("!version"):
                print(show_version(app_version))
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
                        target=send_json,
                        args=(clients[target_addr], file_path_json, END_MARKER),
                    )
                else:
                    thread = Thread(
                        target=send_json,
                        args=(
                            clients[target_addr],
                            file_path_json,
                            lesson_id,
                            END_MARKER,
                        ),
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
                    target=send_leaderboard,
                    args=(clients[target_addr], file_path_json, END_MARKER),
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

    SERVER_IP, SERVER_PORT, IP_TYPE, END_MARKER, outcome = setup(
        app_version, END_MARKER
    )
    if outcome == "shutdown":
        sys_exit(0)

    start_server(SERVER_IP, int(SERVER_PORT), IP_TYPE, END_MARKER)
