from json import loads, dumps
from os.path import join

from utils.server.paths import get_appdata_path
from utils.server.logger import log_error
from utils.server.storage import clean_leaderboard, load_json


# Parses and sends the JSON file to the client.
def send_json(client, file_path, end_marker, id_n=None):

    try:
        file = open(file_path, "rb")
    except FileNotFoundError:
        file_path = str(join(get_appdata_path(), "lessons.json"))
        try:
            file = open(file_path, "rb")
        except FileNotFoundError as fe:
            log_error(fe)
            print("\n[!] No lesson file found!")
            client.sendall(end_marker)
            return

    file.close()

    try:
        data = load_json(file_path)
    except Exception as e:
        print("[!] INVALID JSON! Sending failed!")
        log_error(e)
        client.sendall(end_marker)
        return

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
                print(f"[!] ID {id_s} not found in {file_path}!")

        sending_data = dumps(sending_data)

    client.sendall(sending_data.encode())

    if end_marker in sending_data.encode():
        print(
            f"[!] END MARKER FOUND IN {file_path}, "
            f"SENDING POTENTIALLY CORRUPTED DATA."
        )

    client.sendall(bytes(end_marker))

    file.close()


def send_leaderboard(client, filename, end_marker):

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

    client.sendall(data.encode())

    if end_marker in data.encode():
        print(
            f"[!] END MARKER FOUND IN {filename},"
            f" SENDING POTENTIALLY CORRUPTED DATA."
        )

    client.sendall(bytes(end_marker))
