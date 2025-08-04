from json import JSONDecodeError, loads, dumps, load, dump
from os.path import join, exists as os_path_exists
from threading import Lock

from .paths import get_appdata_path
from .logger import log_error

safe_leaderboard = Lock()


# Parses and sends the JSON file to the client.
def send_json(client, file_path, END_MARKER, id_n=None):

    try:
        file = open(file_path, "r", encoding="utf-8")
    except FileNotFoundError:
        file_path = str(join(get_appdata_path(), "lessons.json"))
        try:
            file = open(file_path, "r", encoding="utf-8")
        except FileNotFoundError as fe:
            log_error(fe)
            print("\n[!] No lesson file found!")
            client.sendall(END_MARKER)
            return

    full_data = file.read()

    try:
        loads(full_data)
    except Exception as e:
        print("[!] INVALID JSON! Sending failed!")
        log_error(e)
        return

    data = loads(full_data)

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

    if END_MARKER in sending_data.encode():
        print(
            f"[!] END MARKER FOUND IN {file_path}, "
            f"SENDING POTENTIALLY CORRUPTED DATA."
        )

    client.sendall(bytes(END_MARKER))

    file.close()


def send_leaderboard(client, filename, END_MARKER):

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

    if END_MARKER in data.encode():
        print(
            f"[!] END MARKER FOUND IN {filename},"
            f" SENDING POTENTIALLY CORRUPTED DATA."
        )

    client.sendall(bytes(END_MARKER))


# Load the leaderboard from the JSON file
def read_leaderboard(filename):
    with safe_leaderboard:
        if not os_path_exists(filename):
            # Create empty file if it doesn't exist
            with open(filename, "w", encoding="utf-8") as f:
                dump([], f)
            return []

        with open(filename, "r", encoding="utf-8") as f:
            return load(f)


def clean_leaderboard(file_path):
    def get_top_n_users(filename, n=10, type_n="points"):
        leaderboard = read_leaderboard(filename)
        # Sort by points descending
        sorted_leaderboard = sorted(leaderboard, key=lambda x: x[type_n], reverse=True)
        return sorted_leaderboard[:n]

    def get_board_types(file_path):

        def create_json():
            with open(file_path, "w", encoding="utf-8") as file:
                json_data = []
                dump(json_data, file, indent=4)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = load(f)

        except FileNotFoundError as fe:
            log_error(fe)
            create_json()

        except JSONDecodeError:
            with open(file_path, "w", encoding="utf-8") as file:
                data = []
                dump(data, file)

        leaderboard_items = []

        for part in data:
            for i in part.keys():
                if i != "username":
                    leaderboard_items.append(i)
            break

        return leaderboard_items

    file_data_types = get_board_types(file_path)
    file_data = []
    for part in file_data_types:
        board_items = get_top_n_users(file_path, 10, str(part))
        for person in board_items:
            found = False
            for file_part in file_data:
                if person["username"] == file_part["username"]:
                    found = True
                    break

            if not found:
                file_data.append(person)

    return dumps(file_data)


def update_leaderboard(username, point_amount, lesson_completed):
    file_name = str(join(get_appdata_path(), "leaderboards.json"))

    # Save the leaderboard to the JSON file
    def write_leaderboard(filename, leaderboard):

        with safe_leaderboard:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    dump(leaderboard, f, indent=4)

            except Exception as e:
                log_error(e)
                return

    # Add or update a user in the leaderboard
    def add_or_update_user(filename, user, points, lessons_completed):
        leaderboard = read_leaderboard(filename)
        found = False

        for entry in leaderboard:
            if entry["username"] == user:
                entry["points"] = points
                entry["lessons_completed"] = lessons_completed
                found = True
                break

        if not found:
            leaderboard.append(
                {
                    "username": user,
                    "points": points,
                    "lessons_completed": lessons_completed,
                }
            )

        write_leaderboard(filename, leaderboard)

    if username == "Unknown":
        return None

    add_or_update_user(file_name, username, point_amount, lesson_completed)
