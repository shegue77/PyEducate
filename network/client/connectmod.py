# Copyright (C) 2025 shegue77
# SPDX-License-Identifier: GPL-3.0-or-later

# ---------------------------[ DEPENDENCIES ]---------------------------
import socket
from getpass import getuser
from threading import Event
from os.path import join
from requests import get

import rsa
from utils.client.paths import get_appdata_path
from utils.client.logger import log_error
from .storage import download_file
from utils.crypto import decrypt_file, encrypt_message, decrypt_message

# ----------------------------------------------------------------------


# -------------------------[ GLOBAL VARIABLES ]-------------------------
client = None
END_MARKER = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"  # End marker used when receiving JSON files, make sure that this end marker MATCHES the end marker on the server.
id_amount = 1
connected_to_server = Event()
pub_key = None
priv_key = None
sym_key = None
# ----------------------------------------------------------------------


# Connects to the server (host).
def start_client(server_ip, server_port, server_type="ipv4"):
    global client
    global pub_key, priv_key, sym_key

    pub_key, priv_key = rsa.newkeys(1024)
    if server_type == "ipv6":
        client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((server_ip, server_port))
    connected_to_server.set()

    # Send public key (RSA)
    client.send(pub_key.save_pkcs1("PEM"))

    # Recieve symmetric AES Fernet key
    sym_key = rsa.decrypt(client.recv(1024), priv_key)

    while True:
        command = decrypt_message(client.recv(1024), sym_key).strip().lower()
        print(f"[Received Command] {command}")

        if command == "!disconnect":
            break

        if command == "!sendjson":
            download_file(client, "json", END_MARKER, sym_key)

        elif command == "!updateboard":
            download_file(client, "board", END_MARKER, sym_key)

        elif command == "!getip":
            try:
                response = get("https://api64.ipify.org?format=json", timeout=5).json()
                client.sendall(encrypt_message(response["ip"].encode(), sym_key))

            except Exception as e:
                log_error(e)
                client.sendall(
                    encrypt_message(
                        "Error retrieving public IP address!".encode(), sym_key
                    )
                )
            continue

        elif command == "!gethostname":
            try:
                name_host = str(socket.gethostname())
                client.sendall(encrypt_message(name_host.encode(), sym_key))

            except Exception as e:
                print(e)
                log_error(e)
                client.sendall(
                    encrypt_message("Error getting hostname!".encode(), sym_key)
                )
            continue

        elif command == "!getusername":
            try:
                username_data = "!getusername " + str(getuser())
                client.sendall(encrypt_message(username_data.encode(), sym_key))

            except Exception as e:
                log_error(e)
                client.sendall(encrypt_message(str(e).encode(), sym_key))

            continue

        elif command == "!getstats":
            stat_path = str(join(get_appdata_path(), "save_data.dat"))
            try:
                with open(stat_path, "rb") as f:
                    data = decrypt_file(f.read()).strip().split()
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
                client.sendall(encrypt_message(username_data.encode(), sym_key))

            except Exception as e:
                print(e)
                log_error(e)

            continue

        else:
            client.sendall(
                encrypt_message("[!] Unrecognised command!".encode(), sym_key)
            )

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
