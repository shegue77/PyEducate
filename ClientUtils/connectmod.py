# Copyright (C) 2025 shegue77
# SPDX-License-Identifier: GPL-3.0-or-later

# ---------------------------[ DEPENDENCIES ]---------------------------
import socket
from getpass import getuser
from threading import Event
from os.path import join
from requests import get

from .paths import get_appdata_path
from .logger import log_error
from .storage import download_file

# ----------------------------------------------------------------------


# -------------------------[ GLOBAL VARIABLES ]-------------------------
client = None
END_MARKER = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"  # End marker used when receiving JSON files, make sure that this end marker MATCHES the end marker on the server.
id_amount = 1
connected_to_server = Event()
# ----------------------------------------------------------------------


# Connects to the server (host).
def start_client(server_ip, server_port, server_type="ipv4"):
    global client
    if server_type == "ipv6":
        client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((server_ip, server_port))
    connected_to_server.set()

    while True:
        print("e")
        command = client.recv(32).decode().strip().lower()
        print(f"[Received Command] {command}")

        if command == "!disconnect":
            break

        if command == "!sendjson":
            print("a")
            download_file(client, "json", END_MARKER)

        elif command == "!updateboard":
            download_file(client, "board", END_MARKER)

        elif command == "!getip":
            try:
                response = get("https://api64.ipify.org?format=json", timeout=5).json()
                client.sendall(response["ip"].encode())

            except Exception as e:
                print(e)
                log_error(e)
                client.sendall("Error retrieving public IP address!".encode())
            continue

        elif command == "!gethostname":
            try:
                name_host = str(socket.gethostname())
                client.sendall(name_host.encode())

            except Exception as e:
                print(e)
                log_error(e)
                client.sendall("Error getting hostname!".encode())
            continue

        elif command == "!getusername":
            try:
                username_data = "!getusername " + str(getuser())
                client.sendall(username_data.encode())

            except Exception as e:
                log_error(e)
                client.sendall(str(e).encode())

            continue

        elif command == "!getstats":
            stat_path = str(join(get_appdata_path(), "SAVE_DATA"))
            try:
                with open(stat_path, "r", encoding="utf-8") as f:
                    data = f.read().strip().split()
                    points = float(data[0])
                    lessons_completed = int(data[1])

            except (
                FileNotFoundError,
                PermissionError,
                IndexError,
                TypeError,
                ValueError,
            ) as ve:
                log_error(ve)
                points = "0"
                lessons_completed = "0"

            full_data = f"{str(points)} {str(lessons_completed)}"

            try:
                username_data = "!getstats " + str(full_data)
                client.sendall(username_data.encode())

            except Exception as e:
                print(e)
                log_error(e)

            continue

        else:
            client.sendall("[!] Invalid command!".encode())

    client.close()
    connected_to_server.clear()


def is_connected():
    return connected_to_server.is_set()


# Closes the client.
def close_client():
    try:
        client.close()

    except Exception:
        pass


# Reads the data about the IP, PORT and IP TYPE (IPv4/IPv6) of the server and connects to the server.
if __name__ == "__main__":
    file_path = join(get_appdata_path(), "connect-data.txt")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            SERVER_IP = str(f.readline().strip().replace("\n", ""))
            SERVER_PORT = int(f.readline().strip())
            IP_TYPE = str(f.readline().strip()).lower()

    except Exception as fe:
        log_error(fe)
        print("[!] Unable to locate save data!\n")
        SERVER_IP = input("Enter server IP (local): ")
        SERVER_PORT = int(input("Enter server port: "))
        IP_TYPE = input("Enter IP type (IPv4/IPv6): ").lower()

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"{SERVER_IP}\n{SERVER_PORT}\n{IP_TYPE}")

    start_client(SERVER_IP, SERVER_PORT, IP_TYPE.lower())
