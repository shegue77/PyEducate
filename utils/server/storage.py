from json import loads, dumps, JSONDecodeError
from os.path import join, exists as os_path_exists
from threading import Lock
from utils.crypto import encrypt_file, decrypt_file

from .paths import get_appdata_path
from .logger import log_error

_safe_leaderboard = Lock()


def write_json(file_path, data):
    with open(file_path, "wb") as f:
        data = dumps(data)
        f.write(encrypt_file(data))


def load_json(file_path):
    with open(file_path, "rb") as f:
        data = loads(decrypt_file(f.read()))
    return data


def find_lesson(lesson_id):
    file_path = join(get_appdata_path(), "lessons.json")

    with open(file_path, "rb") as f:
        data = loads(decrypt_file(f.read()))

    for lesson in data["lessons"]:
        try:
            if int(lesson["id"]) == int(lesson_id):
                for quiz in lesson["quiz"]:  # Loop over the quiz list
                    print(quiz["question"])

                    return (
                        str(lesson["id"]),
                        str(lesson["title"]),
                        str(lesson["image"]),
                        str(lesson["description"]),
                        str(lesson["content"]),
                        str(quiz["question"]),
                        str(quiz["answer"]),
                    )
        except Exception as e:
            log_error(e)
            return None


def list_lessons():
    file_path = join(get_appdata_path(), "lessons.json")
    try:
        with open(file_path, "rb") as f:
            data = loads(decrypt_file(f.read()))

    except FileNotFoundError:
        with open(file_path, "wb") as f:
            data = {"lessons": []}
            f.write(encrypt_file(dumps(data)))

    whole_data = ""
    for lesson in data["lessons"]:
        whole_data += f'Title: {lesson["title"]} | ID: {lesson["id"]}\n'

    return whole_data


# Load the leaderboard from the JSON file
def read_leaderboard(filename):
    with _safe_leaderboard:
        if not os_path_exists(filename):
            # Create empty file if it doesn't exist
            with open(filename, "wb") as f:
                json_data = []
                f.write(encrypt_file(dumps(json_data)))
            return []

        with open(filename, "rb") as f:
            return loads(decrypt_file(f.read()))


def clean_leaderboard(file_path):
    def get_top_n_users(filename, n=10, type_n="points"):
        leaderboard = read_leaderboard(filename)
        # Sort by points descending
        sorted_leaderboard = sorted(leaderboard, key=lambda x: x[type_n], reverse=True)
        return sorted_leaderboard[:n]

    def get_board_types(file_path):

        def create_json():
            with open(file_path, "wb") as file:
                json_data = []
                file.write(encrypt_file(dumps(json_data)))

        try:
            with open(file_path, "rb") as f:
                data = loads(decrypt_file(f.read()))

        except FileNotFoundError as fe:
            log_error(fe)
            create_json()

        except JSONDecodeError:
            with open(file_path, "wb") as file:
                data = []
                file.write(encrypt_file(dumps(data)))

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
    def _write_leaderboard(filename, leaderboard):

        with _safe_leaderboard:
            try:
                with open(filename, "wb") as f:
                    leaderboard = dumps(leaderboard)
                    f.write(encrypt_file(leaderboard))

            except Exception as e:
                log_error(e)
                return

    # Add or update a user in the leaderboard
    def _add_or_update_user(filename, user, points, lessons_completed):
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

        _write_leaderboard(filename, leaderboard)

    if username == "Unknown":
        return None

    _add_or_update_user(file_name, username, point_amount, lesson_completed)
