# Copyright (C) 2025 shegue77
# SPDX-License-Identifier: GPL-3.0-or-later
__version__ = '1.0.0-rc0'

# ---------------------------[ DEPENDENCIES ]---------------------------
import socket
from getpass import getuser
from threading import Event
from os import getenv, makedirs
from os.path import exists as os_path_exists, expanduser
from json import load, loads, dump, JSONDecodeError
from datetime import datetime
from requests import get
from platform import system
# ----------------------------------------------------------------------


# -------------------------[ GLOBAL VARIABLES ]-------------------------
client = None
end_marker = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>" # End marker used when receiving JSON files, make sure that this end marker MATCHES the end marker on the server.
id_amount = 1
connected_to_server = Event()
# ----------------------------------------------------------------------


# Function gets the full path to APPDATA.
def get_appdata_path():
    user_os = system()
    if user_os == 'Windows':
        path_to_appdata = getenv('APPDATA')
    elif user_os == 'Darwin':
        path_to_appdata = expanduser('~/Library/Application Support')
    else:
        path_to_appdata = getenv('XDG_DATA_HOME', expanduser('~/.local/share'))

    if os_path_exists(path_to_appdata + "\\PyEducate"):
        if os_path_exists(path_to_appdata + "\\PyEducate\\client"):
            full_path_data = path_to_appdata + "\\PyEducate\\client"
        else:
            makedirs(path_to_appdata + "\\PyEducate\\client")
            full_path_data = path_to_appdata + "\\PyEducate\\client"
    else:
        makedirs(path_to_appdata + "\\PyEducate")
        makedirs(path_to_appdata + "\\PyEducate\\client")
        full_path_data = path_to_appdata + "\\PyEducate\\client"

    return full_path_data

def log_error(data):

    # Get current time
    now = datetime.now()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    log_path = str(get_appdata_path() + '\\client-module.log')

    data = str(timestamp + ' ' + str(data) + '\n')

    try:
        with open(log_path, 'a') as f:
            f.write(data)

    except FileNotFoundError:
        with open(log_path, 'w') as f:
            f.write(data)

    except PermissionError:
        print(f'[!] Insufficient permissions!\nUnable to log data at {log_path}!')


# After download, the downloaded lesson gets sent here to be added to the JSON file containing locally-stored lessons.
def get_json_file(new_lessons):
    file_path = get_appdata_path() + '\\lessons.json'

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = load(file)

    except FileNotFoundError:
        data = {"lessons": []}

    lessons = data["lessons"]

    if isinstance(new_lessons, str):
        try:
            new_lessons = loads(new_lessons)
        except JSONDecodeError as e:
            log_error(e)
            print("❌ Invalid JSON string:", e)
            return None

    if not isinstance(new_lessons, list):
        print("❌ Input must be a list of lessons.")
        return None

    for lesson in new_lessons:
        lesson["id"] = len(lessons) + 1
        lessons.append(lesson)

    with open(file_path, 'w', encoding='utf-8') as f:
        dump({"lessons": lessons}, f, indent=4)

    print(f"✅ Added {len(new_lessons)} lessons.")
    return "SUCCESS"


# Downloads the lesson from the server (host).
def download_file(client_r, mode):

    print("Listening for data...")

    if mode == 'json':
        file_path = get_appdata_path() + '\\temp-lessons.json'
    else:
        file_path = get_appdata_path() + '\\temp-leaderboards.json'

    file = open(file_path, 'wb')
    file_bytes = b""
    done = False

    while not done:
        if file_bytes[-34:] == bytes(end_marker):
            done = True
            file_bytes = file_bytes[:-34]
            break

        print('Receiving data')
        print(file_bytes)
        data = client_r.recv(1024)

        if file_bytes[-34:] == bytes(end_marker):
            done = True
            file_bytes = file_bytes[:-34]

        else:
            file_bytes += data

        print('Updated')

    file.write(file_bytes)
    file.close()

    lesson = open(file_path, 'r', encoding='utf-8').read()
    print(lesson)
    print(mode)

    if mode == 'json':
        get_json_file(lesson)

    else:
        try:
            lesson = loads(lesson)
        except JSONDecodeError as e:
            log_error(e)
            print("❌ Invalid JSON string:", e)
            return None

        with open(str(get_appdata_path() + '\\leaderboards.json'), 'w') as f:
            dump(lesson, f)


# Connects to the server (host).
def start_client(server_ip, server_port, server_type='ipv4'):
    global client
    if server_type == 'ipv6':
        client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((server_ip, server_port))
    connected_to_server.set()

    while True:
        print('e')
        command = client.recv(32).decode().strip().lower()
        print(f"[Received Command] {command}")

        if command == "!disconnect":
            break

        elif command == "!sendjson":
            print('a')
            download_file(client, 'json')
            continue

        elif command == "!updateboard":
            download_file(client, 'board')

        elif command == "!getip":
            try:
                response = get('https://api64.ipify.org?format=json').json()
                client.sendall(response['ip'].encode())

            except Exception as e:
                print(e)
                log_error(e)
                client.sendall('Error retrieving public IP address!'.encode())
            continue

        elif command == "!gethostname":
            try:
                name_host = str(socket.gethostname())
                client.sendall(name_host.encode())

            except Exception as e:
                print(e)
                log_error(e)
                client.sendall('Error getting hostname!'.encode())
            continue

        elif command == "!getusername":
            try:
                username_data = '!getusername ' + str(getuser())
                client.sendall(username_data.encode())

            except Exception as e:
                log_error(e)
                client.sendall(str(e).encode())

            continue

        elif command == "!getstats":
            stat_path = str(get_appdata_path() + '\\SAVE_DATA')
            try:
                with open(stat_path, 'r') as f:
                    data = f.read().strip().split()
                    points = int(data[0])
                    lessons_completed = int(data[1])

            except (FileNotFoundError, PermissionError, IndexError, TypeError, ValueError) as ve:
                log_error(ve)
                points = '0'
                lessons_completed = '0'

            full_data = f'{str(points)} {str(lessons_completed)}'

            try:
                username_data = '!getstats ' + str(full_data)
                client.sendall(username_data.encode())

            except Exception as e:
                log_error(e)

            continue

        else:
            client.sendall('[!] Invalid command!'.encode())


    client.close()
    connected_to_server.clear()

def is_connected():
    return connected_to_server.is_set()

# Closes the client.
def close_client():
    global client
    try:
        client.close()

    except Exception:
        pass


# Reads the data about the IP, PORT and IP TYPE (IPv4/IPv6) of the server and connects to the server.
if __name__ == "__main__":
    file_path = get_appdata_path() + '\\connect-data.txt'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            SERVER_IP = str(f.readline().strip().replace('\n', ''))
            SERVER_PORT = int(f.readline().strip())
            IP_TYPE = str(f.readline().strip()).lower().encode()

    except Exception as fe:
        log_error(fe)
        print('[!] Unable to locate save data!\n')
        SERVER_IP = input("Enter server IP (local): ")
        SERVER_PORT = input("Enter server port: ")
        IP_TYPE = input("Enter IP type (IPv4/IPv6): ").lower()

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"{SERVER_IP}\n{SERVER_PORT}\n{IP_TYPE}")


    start_client(SERVER_IP, SERVER_PORT, IP_TYPE.lower())