from json import loads, dumps, JSONDecodeError
from os.path import join, exists as os_path_exists
from threading import Lock
from utils.crypto import (
    encrypt_file,
    decrypt_file,
    encrypt_with_password,
    decrypt_with_password,
    get_signature,
)

from .paths import get_appdata_path
from .logger import log_error

_safe_leaderboard = Lock()


def _validate_lesson(lesson_data):
    from utils.crypto import verify_signature

    lesson_data = loads(lesson_data)
    lesson_data = lesson_data["lessons"]

    valid_ids = {}

    for lesson in lesson_data:
        sign64 = lesson["signature"]
        lesson.pop("signature", None)
        lesson_id = lesson["id"]
        del lesson["id"]
        if verify_signature(dumps(lesson), sign64):
            valid_ids.update({int(lesson_id): True})
        else:
            valid_ids.update({int(lesson_id): False})
    return valid_ids


def import_file(self):
    try:
        from PySide6.QtWidgets import QFileDialog, QInputDialog
    except ModuleNotFoundError as me:
        log_error(me)
        return
    file_path, _ = QFileDialog.getOpenFileName(
        self, "Import File", "", "Lesson Files (*.json);;All Files (*)"
    )
    if file_path:
        dialog = QInputDialog()
        dialog.setWindowTitle("Password-protection")
        dialog.setLabelText("Enter file password:")
        dialog.setOkButtonText("Submit Password")
        dialog.setCancelButtonText("No Password")

        # Execute the dialog
        if dialog.exec() == QInputDialog.Accepted:
            password = dialog.textValue()
            try:
                lesson_data = decrypt_with_password(
                    open(file_path, "rb").read(), password
                )
                print(_validate_lesson(lesson_data))
            except (FileNotFoundError, PermissionError, JSONDecodeError) as fe:
                log_error(fe)
                print(fe)
                return
        else:
            try:
                lesson_data = open(file_path, "rb").read().decode("utf-8")
                print(_validate_lesson(lesson_data))
            except (FileNotFoundError, PermissionError, JSONDecodeError) as fe:
                log_error(fe)
                print(fe)
                return
        merge_lessons(lesson_data)


def export_file(self):
    try:
        from PySide6.QtWidgets import QFileDialog, QInputDialog
    except ModuleNotFoundError as me:
        log_error(me)
        return
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Export File", "", "Lesson Files (*.json);;All Files (*)"
    )
    try:
        with open(join(get_appdata_path(), "lessons.json"), "rb") as f:
            lesson_data = decrypt_file(f.read().decode("utf-8"))
    except (FileNotFoundError, PermissionError) as fe:
        log_error(fe)
        return
    if file_path:
        # Password
        dialog = QInputDialog()
        dialog.setWindowTitle("Password-protection")
        dialog.setLabelText("Enter secure password (REMEMBER PASSWORD):")
        dialog.setOkButtonText("Submit Password")
        dialog.setCancelButtonText("No Password")

        lesson_data = loads(lesson_data)
        for lesson in lesson_data["lessons"]:
            lesson_id = lesson["id"]
            del lesson["id"]
            lesson.pop("signature", None)
            lesson["signature"] = get_signature(dumps(lesson))
            lesson["id"] = lesson_id
        lesson_data = dumps(lesson_data)

        # Execute the dialog
        if dialog.exec() == QInputDialog.Accepted:
            password = dialog.textValue()
            with open(file_path, "wb") as f:
                f.write(encrypt_with_password(lesson_data, password))
        else:
            with open(file_path, "wb") as f:
                f.write(lesson_data.encode("utf-8"))

        print("Exported:", file_path)


def merge_lessons(new_lessons):
    file_path = join(get_appdata_path(), "lessons.json")

    try:
        data = load_json(file_path)

    except (FileNotFoundError, JSONDecodeError):
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

        if isinstance(new_lessons, dict):
            lesson_count = 0
            for lesson in new_lessons["lessons"]:
                lesson["id"] = len(lessons) + 1
                lessons.append(lesson)
                lesson_count += 1
            print(f"✅ Added {lesson_count} lessons.")
        else:
            return None
    else:
        print("❌ Input must be a list/dict of lessons.")
        for lesson in new_lessons:
            lesson["id"] = len(lessons) + 1
            lessons.append(lesson)
        print(f"✅ Added {len(new_lessons)} lessons.")

    write_json(file_path, data)
    return "SUCCESS"


def lesson_req_checks(all_texts):
    title = all_texts[0].text()
    mild_desc = str(all_texts[1].text())
    content = str(all_texts[3].toPlainText())
    question = str(all_texts[4].text())
    answer = str(all_texts[5].toPlainText())

    required_texts = (title, mild_desc, content, question, answer)

    for text in required_texts:
        if text.strip() == "":
            return False

    return True


def get_username():
    full_path = get_appdata_path()
    with open(join(full_path, "save_data.dat"), "rb") as f:
        username = decrypt_file(f.read())
    return username


def del_lesson(id_input):
    file_path = join(get_appdata_path(), "lessons.json")

    data = load_json(file_path)

    for lesson in data["lessons"]:
        for id_num in str(lesson["id"]):
            if str(id_num) == str(id_input):
                data["lessons"].remove(lesson)
                write_json(file_path, data)
                print(f"Lesson with ID {id_num} is being deleted...")

    existing_ids = []

    for lesson in data["lessons"]:
        for id_num in str(lesson["id"]):
            existing_ids.append(str(id_num))

    try:
        if int(id_input) not in existing_ids:
            return True
        else:
            return False

    except Exception as e:
        log_error(e)

    return False


def create_json(id_input, all_texts):
    file_path = join(get_appdata_path(), "lessons.json")

    did_pass = lesson_req_checks(all_texts)

    if not did_pass:
        print("Not all required fields have been filled out!")
        return "Halt"

    title = all_texts[0].text()
    mild_desc = str(all_texts[1].text())
    points = str(all_texts[2].text())
    content = str(all_texts[3].toPlainText())
    question = str(all_texts[4].text())
    answer = str(all_texts[5].toPlainText())
    try:
        image = str(all_texts[6].text())
    except IndexError:
        image = ""

    quiz = [{"question": question, "answer": answer}]

    def read_lesson(id_input):
        lesson_path = join(get_appdata_path(), "lessons.json")

        try:
            json_data = load_json(lesson_path)
            print(json_data)

        except FileNotFoundError as fe:
            log_error(fe)
            return True

        for lesson in json_data["lessons"]:
            if str(lesson["id"]) == str(id_input):
                return False

        return True

    while True:
        response = read_lesson(id_input)
        print(id_input)
        if response:
            break
        else:
            id_input += 1

    new_lesson = dumps(
        {
            "id": str(id_input),
            "title": title,
            "description": mild_desc,
            "image": image,
            "content": content,
            "points": points,
            "quiz": quiz,
        }
    )

    try:
        new_lesson = loads(new_lesson)
        print("✅ JSON is valid")
    except JSONDecodeError as e:
        print("❌ Invalid JSON:", e)
        log_error(e)
        return None

    lesson_id = new_lesson["id"]
    del new_lesson["id"]
    signature = get_signature(dumps(new_lesson))
    new_lesson["id"] = lesson_id
    new_lesson["signature"] = signature

    # Load from file
    try:
        data = load_json(file_path)

    except FileNotFoundError:
        data = {"lessons": []}

    # Modify (e.g., add a lesson)
    data["lessons"].append(new_lesson)

    # Save back to file
    write_json(file_path, data)
    return id_input


def write_json(file_path, data):
    with open(file_path, "wb") as f:
        data = dumps(data)
        f.write(encrypt_file(data))


def load_json(file_path):
    with open(file_path, "rb") as f:
        data = loads(decrypt_file(f.read()))
    return data


def write_save_data(host, port, ip_type, username_setting):
    full_path = get_appdata_path()
    with open(join(full_path, "connect-data.txt"), "wb") as f:
        data = f"{port}\n{ip_type}\n{host}"
        data = encrypt_file(data)
        f.write(data)

    with open(join(full_path, "save_data.dat"), "wb") as f:
        data = encrypt_file(str(username_setting))
        f.write(data)


def find_lesson(lesson_id):
    file_path = join(get_appdata_path(), "lessons.json")

    data = load_json(file_path)

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
                        str(lesson["points"]),
                    )
        except Exception as e:
            log_error(e)
            return None
    return None


def list_lessons(error_message: str = "No lessons found!"):
    file_path = join(get_appdata_path(), "lessons.json")
    try:
        data = load_json(file_path)

    except FileNotFoundError:
        data = {"lessons": []}
        write_json(file_path, data)

    whole_data = ""
    if data["lessons"]:
        for lesson in data["lessons"]:
            whole_data += f'Title: {lesson["title"]} | ID: {lesson["id"]}\n'
    else:
        whole_data = error_message

    return whole_data


# Load the leaderboard from the JSON file
def read_leaderboard(filename):
    with _safe_leaderboard:
        if not os_path_exists(filename):
            # Create empty file if it doesn't exist
            write_json(filename, [])
            return []

        return load_json(filename)


def clean_leaderboard(file_path):
    def get_top_n_users(filename, n=10, type_n="points"):
        leaderboard = read_leaderboard(filename)
        # Sort by points descending
        sorted_leaderboard = sorted(leaderboard, key=lambda x: x[type_n], reverse=True)
        return sorted_leaderboard[:n]

    def get_board_types(file_path):

        try:
            with open(file_path, "rb") as f:
                data = loads(decrypt_file(f.read()))

        except (FileNotFoundError, JSONDecodeError) as fe:
            log_error(fe)
            write_json(file_path, [])

        leaderboard_items = []

        for item in data:
            for i in item.keys():
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
                write_json(filename, leaderboard)

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
    return None
