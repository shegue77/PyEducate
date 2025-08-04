from json import load, loads, dump, JSONDecodeError
from os.path import join
from .paths import get_appdata_path
from .logger import log_error


# After download, the downloaded lesson gets sent here to be added to the JSON file containing locally-stored lessons.
def get_json_file(new_lessons):
    file_path = join(get_appdata_path(), "lessons.json")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
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

    with open(file_path, "w", encoding="utf-8") as f:
        dump({"lessons": lessons}, f, indent=4)

    print(f"✅ Added {len(new_lessons)} lessons.")
    return "SUCCESS"


# Downloads the lesson from the server (host).
def download_file(client_r, mode, END_MARKER):

    print("Listening for data...")

    if mode == "json":
        file_path = join(get_appdata_path(), "temp-lessons.json")
    else:
        file_path = join(get_appdata_path(), "temp-leaderboards.json")

    file = open(file_path, "wb")
    file_bytes = b""
    done = False

    while not done:
        if file_bytes[-34:] == bytes(END_MARKER):
            done = True
            file_bytes = file_bytes[:-34]
            break

        print("Receiving data")
        print(file_bytes)
        data = client_r.recv(1024)

        if file_bytes[-34:] == bytes(END_MARKER):
            done = True
            file_bytes = file_bytes[:-34]

        else:
            file_bytes += data

        print("Updated")

    file.write(file_bytes)
    file.close()

    lesson = open(file_path, "r", encoding="utf-8").read()
    print(lesson)
    print(mode)

    if mode == "json":
        get_json_file(lesson)

    else:
        try:
            lesson = loads(lesson)
        except JSONDecodeError as e:
            log_error(e)
            print("❌ Invalid JSON string:", e)
            return None

        with open(
            str(join(get_appdata_path(), "leaderboards.json")), "w", encoding="utf-8"
        ) as f:
            dump(lesson, f)
