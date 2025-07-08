# Connects the client to the server

# ---------------------------[ DEPENDENCIES ]---------------------------
import socket
from os import getenv, makedirs
from os.path import exists as os_path_exists
from json import load, loads, dump, JSONDecodeError
from requests import get
# ----------------------------------------------------------------------


# -------------------------[ GLOBAL VARIABLES ]-------------------------
client = None
end_marker = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>" # End marker used when receiving JSON files, make sure that this end marker MATCHES the end marker on the server.
id_amount = 1
# ----------------------------------------------------------------------


# Function gets the full path to APPDATA.
def get_appdata_path():
    path_to_appdata = getenv('APPDATA')
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
def download_file(client_r):

    print("Listening for data...")

    file_path = get_appdata_path() + '\\temp-lessons.json'

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

    get_json_file(lesson)


# Connects to the server (host).
def start_client(server_ip, server_port, server_type='ipv4'):
    global client
    if server_type == 'ipv6':
        client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((server_ip, server_port))

    while True:
        print('e')
        command = client.recv(32).decode()
        print(f"[Received Command] {command}")

        if command.strip().lower() == "!disconnect":
            break

        if command.lower() == "!sendjson":
            print('a')
            download_file(client)
            continue

        if command.lower() == "!getip":
            try:
                response = get('https://api64.ipify.org?format=json').json()
                client.sendall(response['ip'].encode())
            except Exception as e:
                print(e)
                client.sendall('Error retrieving public IP address!'.encode())
            continue

    client.close()

# Closes the client.
def close_client():
    global client
    try:
        client.close()
    except Exception:
        pass
    client = None


# Reads the data about the IP, PORT and IP TYPE (IPv4/IPv6) of the server and connects to the server.
if __name__ == "__main__":
    file_path = get_appdata_path() + '\\connect-data.txt'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            SERVER_IP = str(f.readline().strip().replace('\n', ''))
            SERVER_PORT = int(f.readline().strip())
            IP_TYPE = str(f.readline().strip()).lower()
    except FileNotFoundError:
        print('[!] Unable to locate save data!\n')
        SERVER_IP = input("Enter server IP (IPv4/IPv6): ")
        SERVER_PORT = input("Enter server port: ")
        IP_TYPE = input("Enter IP type (IPv4/IPv6): ").lower()

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"{SERVER_IP}\n{SERVER_PORT}\n{IP_TYPE}")


    start_client(SERVER_IP, SERVER_PORT, IP_TYPE.lower())