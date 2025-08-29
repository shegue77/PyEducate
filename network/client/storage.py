from json import loads, JSONDecodeError
from os.path import join
from utils.client.paths import get_appdata_path
from utils.client.logger import log_error
from utils.crypto import decrypt_file, encrypt_file
from utils.client.storage import load_json, write_json


# After download, the downloaded lesson gets sent here to be added to the JSON file containing locally-stored lessons.
def _get_json_file(new_lessons):
    file_path = join(get_appdata_path(), "lessons.json")

    try:
        data = load_json(file_path)

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

    write_json(file_path, data)
    print(f"✅ Added {len(new_lessons)} lessons.")
    return "SUCCESS"


# Downloads the lesson from the server (host).
def download_file(client_r, mode, end_marker):

    print("Listening for data...")

    if mode == "json":
        file_path = join(get_appdata_path(), "temp-lessons.json")
    else:
        file_path = join(get_appdata_path(), "temp-leaderboards.json")

    file = open(file_path, "wb")
    file_bytes = b""

    while True:
        if file_bytes[-len(end_marker) :] == bytes(end_marker):
            file_bytes = file_bytes[:-34]
            break

        print("Receiving data")
        data = client_r.recv(1024)

        if file_bytes[-34:] == bytes(end_marker):
            file_bytes = file_bytes[:-34]
            print("Updated")
            break

        else:
            file_bytes += data
            print("Updated")

    file.write(encrypt_file(file_bytes))
    file.close()

    ciphertext = open(file_path, "rb").read()
    lesson = decrypt_file(ciphertext)

    if mode == "json":
        _get_json_file(lesson)

    else:
        try:
            lesson = loads(lesson)
        except JSONDecodeError as e:
            log_error(e)
            print("❌ Invalid JSON string:", e)
            return

        write_json(join(get_appdata_path(), "leaderboards.json"), lesson)
