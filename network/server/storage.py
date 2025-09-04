from json import loads, dumps
from os.path import join

from utils.crypto import encrypt_message
from utils.server.paths import get_appdata_path
from utils.server.logger import log_error
from utils.server.storage import clean_leaderboard, load_json


# Parses and sends the JSON file to the client.
def send_json(client, file_path, end_marker, sym_key=b"", id_n=None) -> None:

    try:
        file = open(file_path, "rb")
    except FileNotFoundError:
        file_path = str(join(get_appdata_path(), "lessons.json"))
        try:
            file = open(file_path, "rb")
        except FileNotFoundError as fe:
            log_error(fe)
            print("\n[!] No lesson file found!")
            if not sym_key:
                client.sendall(end_marker)
            else:
                client.sendall(encrypt_message(end_marker, sym_key))
            return

    file.close()

    try:
        data = load_json(file_path)
    except Exception as e:
        print("[!] INVALID JSON! Sending failed!")
        log_error(e)
        if not sym_key:
            client.sendall(end_marker)
        else:
            client.sendall(encrypt_message(end_marker, sym_key))
        return

    if id_n is None:
        sending_data: str = dumps(data.get("lessons", []))

    else:
        id_n = list(id_n)
        data_send: list = []

        for id_s in id_n:
            id_found = False
            for lesson in data["lessons"]:
                if int(lesson["id"]) == int(id_s):
                    data_send.append(lesson)
                    id_found = True
                    break

            if not id_found:
                print(f"[!] ID {id_s} not found in {file_path}!")

        sending_data = dumps(data_send)

    if sym_key:
        client.sendall(encrypt_message(sending_data.encode(), sym_key))
    else:
        client.sendall(sending_data.encode())

    if end_marker in sending_data.encode():
        print(
            f"[!] END MARKER FOUND IN {file_path}, "
            f"SENDING POTENTIALLY CORRUPTED DATA."
        )

    if sym_key:
        client.sendall(encrypt_message(bytes(end_marker), sym_key))
    else:
        client.sendall(end_marker)

    file.close()


def send_leaderboard(client, filename, end_marker, sym_key=b"") -> None:

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
        log_error(e)
        return

    data = loads(full_data)
    data = dumps(data)

    if not sym_key:
        client.sendall(data.encode())
    else:
        client.sendall(encrypt_message(data.encode(), sym_key))

    print("sent")
    if end_marker in data.encode():
        print(
            f"[!] END MARKER FOUND IN {filename},"
            f" SENDING POTENTIALLY CORRUPTED DATA."
        )

    if sym_key:
        client.sendall(encrypt_message(bytes(end_marker), sym_key))
    else:
        client.sendall(end_marker)
