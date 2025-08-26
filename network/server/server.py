# Copyright (C) 2025 shegue77
# SPDX-License-Identifier: GPL-3.0-or-later

# ---------------------------[ DEPENDENCIES ]---------------------------
import socket
from threading import Thread
from os.path import join
from schedule import every, run_pending

from PySide6.QtWidgets import QTextEdit

from utils.server.paths import get_appdata_path
from utils.server.logger import log_error
from utils.server.admin import ban_user, unban_user, check_if_banned, list_banned
from utils.server.help import show_version, show_license, help_data
from utils.server.storage import update_leaderboard
from network.server.storage import send_leaderboard, send_json
from network.server.network import get_local_ip_address, validate_ip

# ----------------------------------------------------------------------


# -------------------------[ GLOBAL VARIABLES ]-------------------------
app_version = "v2.0.0"
clients: dict = {}  # Keeps track of clients
server = None
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
def handle_client(client_socket, addr, self):
    if check_if_banned(addr):
        client_socket.send("!disconnect".encode())
        client_socket.close()
        clients.pop(addr, None)
        usernames.pop(addr, None)
        return None

    clients[addr] = client_socket

    server_output: QTextEdit = self.findChild(QTextEdit, "server_output")

    print(f"[!] {addr[0]} connected.")
    server_output.append(f"[!] {addr[0]} connected.")

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
                server_output.append("[*] Updated stats.")

            else:
                print(f"\n[{addr[0]} Output]: {response}")
                server_output.append(f"\n[{addr[0]} Output]: {response}")

        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            break

    print(f"[!] Client {addr[0]} disconnected.")
    server_output.append(f"[!] Client {addr[0]} disconnected.")
    client_socket.close()
    del clients[addr]
    usernames.pop(addr, None)


# Stops the server
def disconnect():
    global server

    for client in clients.values():
        client.send("!disconnect".encode())
        client.close()

    try:
        server.close()
        server = None
    except Exception as e:
        log_error(e)
        print(e)

    print("disconnected")


# Starts the server and listens for clients.
def start_server(host, port, self, server_type="ipv4"):
    global server
    server_output: QTextEdit = self.findChild(QTextEdit, "server_output")
    server_output.setText("")

    if server_type == "ipv6":
        server_local = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        if str(host).strip() == "":
            get_local_ip_address(server_type)
            server_output.append(
                "[!] Invalid IPv6 address!\n" "Defaulting to automatic IP.\n"
            )
    else:
        server_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not validate_ip(host):
            get_local_ip_address(server_type)
            server_output.append(
                "[!] Invalid IPv4 address!\n" "Defaulting to automatic IP.\n"
            )

    try:
        server_local.bind((host, port))
    except Exception as e:
        log_error(e)
        print(e)
        disconnect()
        return

    server = server_local
    server.listen()
    print(show_version(app_version))
    server_output.append(show_version(app_version))
    print("Press the 'enter' key to refresh client list " "& the command prompt.\n")
    print(
        "For more help about the commands of this application, "
        "run !help to view all commands with explanations.\n"
    )
    server_output.append(
        "For more help about the commands of this application, "
        "run !help to view all commands with explanations.\n"
    )
    print(f"[*] Listening on {host}:{port}")
    server_output.append(f"[*] Listening on {host}:{port}")

    # Start accepting client connections
    Thread(target=accept_clients, args=(server, self), daemon=True).start()
    print("Server started successfully")
    every(30).seconds.do(
        lambda: server_output.append("Waiting for clients to connect...")
    )


# Function to accept incoming client connections
def accept_clients(server, self):
    try:
        while True:
            client_socket, addr = server.accept()
            Thread(
                target=handle_client, args=(client_socket, addr, self), daemon=True
            ).start()

    except OSError:
        pass


def show_clients_list(client_list):
    print("\n[Connected Clients]")
    client_list.setText("")

    for idx, addr in enumerate(clients.keys(), start=1):
        username = usernames.get(addr, "Unknown")
        print(f"{idx}. {addr[0]} - {username}")
        client_list.append(f"{idx}. {addr[0]} - {username}\n")


# Function to process commands and communicate with the client
def process_command(self, server_data, command, choice):
    server_output: QTextEdit = self.findChild(QTextEdit, "server_output")
    client_list: QTextEdit = self.findChild(QTextEdit, "client_list")

    if not clients:
        run_pending()
        if str(command).strip().lower().startswith("!help") or str(
            command
        ).strip().lower().startswith("help"):
            print(help_data())
            server_output.append(help_data())
        elif str(command).strip().lower().startswith("!info"):
            server_output.append(
                "\n"
                f"SERVER IP: {server_data[0]}\n"
                f"SERVER PORT: {server_data[1]}\n"
                f"IP TYPE: {server_data[2]}\n"
                f"End marker: {str(END_MARKER)}\n"
                f"Log file: {str(join(get_appdata_path(), 'server.log'))}"
            )
        elif str(command).strip().lower().startswith("!ban"):
            response = ban_user(str(command).strip().lower())
            server_output.append(response)
        elif str(command).strip().lower().startswith("!unban"):
            try:
                ip_address = str(command).strip().lower().split()[1]
            except Exception:
                print("[!] IP address not specified! " "Unable to unban user!")
                server_output.append(
                    "[!] IP address not specified! " "Unable to unban user!"
                )
                return

            response = unban_user(ip_address)
            server_output.append(response)

        elif str(command).strip().lower().startswith("!version"):
            server_output.append(show_version(app_version))
        elif str(command).strip().lower().startswith("!license"):
            server_output.append(show_license())
        elif str(command).strip().lower().startswith("!showblacklist"):
            server_output.append(list_banned())
        elif str(command).strip().lower().startswith("!shutdown"):
            disconnect()
        return

    show_clients_list(client_list)

    try:
        choice = int(choice) - 1

    except ValueError:
        server_output.append("\n[!] Invalid choice!")
        return

    if choice == -1:
        # Broadcast command to all clients

        if command.startswith("!help") or command.startswith("help"):
            server_output.append(help_data())

        elif command.startswith("!shutdown"):
            disconnect()

        elif command.startswith("!info"):
            server_output.append(
                f"SERVER IP: {server_data[0]}\n"
                f"SERVER PORT: {server_data[1]}\n"
                f"IP TYPE: {server_data[2]}\n"
                f"End marker: {str(server_data[3])}\n"
            )

        elif command == "":
            return

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
                server_output.append("\n[*] Updated leaderboard")

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
                        server_output.append("[!] LESSON ID NOT SPECIFIED!")
                        return

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
                server_output.append("\n[*] Sent lessons")

        elif command.startswith("!showblacklist"):
            server_output.append(list_banned())

        elif command.startswith("!version"):
            server_output.append(show_version(app_version))
        elif command.startswith("!license"):
            server_output.append(show_license())

        elif command.startswith("!ban"):
            response = ban_user(command)
            server_output.append(response)

        elif command.startswith("!unban"):
            try:
                ip_address = str(choice).strip().lower().split()[1]
            except Exception:
                server_output.append(
                    "[!] IP address not specified! " "Unable to unban user!"
                )
                return

            response = unban_user(ip_address)
            server_output.append(response)

        elif command.startswith("!getstats"):
            server_output.append("[*] Updating stats...")
            for client in clients.values():
                client.sendall(command.encode())

        else:
            for client in clients.values():
                client.sendall(command.encode())

    elif 0 <= choice < len(clients):
        target_addr = list(clients.keys())[choice]

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
                    server_output.append("[!] LESSON ID NOT SPECIFIED!")
                    return

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
            server_output.append("\n[*] Sent lessons")

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
            server_output.append("\n[*] Updated leaderboard")

        elif command == "":
            return

        elif command.startswith("!help"):
            print(help_data())
            server_output.append(help_data())

        elif command.startswith("!info"):
            print(
                f"SERVER IP: {server_data[0]}\n"
                f"SERVER PORT: {server_data[1]}\n"
                f"IP TYPE: {server_data[2]}\n"
                f"End marker: {str(server_data[3])}\n"
            )

            server_output.append(
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

            server_output.append(
                "[!] Unsupported command,"
                "please use broadcast to run !shutdown.\n"
                "Did you mean !exit?"
            )

        elif command.startswith("!showblacklist"):
            print(list_banned())
            server_output.append(list_banned())

        elif command.startswith("!ban"):
            response = ban_user(command)
            server_output.append(response)

        elif command.startswith("!unban"):
            try:
                ip_address = str(choice).strip().lower().split()[1]
            except Exception:
                print("[!] IP address not specified!" "Unable to unban user!")
                server_output.append(
                    "[!] IP address not specified!" "Unable to unban user!"
                )
                return

            response = unban_user(ip_address)
            server_output.append(response)

        elif command.startswith("!getstats"):
            server_output.append("[*] Updating stats...")
            clients[target_addr].sendall(command.encode())

        else:
            clients[target_addr].sendall(command.encode())

    else:
        print("[!] Invalid selection.")
        server_output.append("[!] Invalid selection.")
