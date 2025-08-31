from json import loads, dumps, JSONDecodeError
from os.path import join
from os import makedirs
from .paths import get_appdata_path
from .logger import log_error
from utils.crypto import decrypt_file, encrypt_file, decrypt_with_password


def write_json(file_path, data):
    with open(file_path, "wb") as f:
        data = dumps(data)
        f.write(encrypt_file(data))


def load_json(file_path):
    with open(file_path, "rb") as f:
        data = loads(decrypt_file(f.read()))
    return data


def get_username():
    full_path = get_appdata_path()
    with open(join(full_path, "username.dat"), "rb") as f:
        username = decrypt_file(f.read())
    return username


def mark_lesson_finish(lesson_id):
    file_path = join(get_appdata_path(), "lessons.json")
    try:
        data = load_json(file_path)

    except (FileNotFoundError, JSONDecodeError) as fe:
        print(fe)
        print()
        makedirs(join(get_appdata_path(), "images"), exist_ok=True)

        data = {"lessons": []}
        write_json(file_path, data)
        return None

    for lesson in data["lessons"]:
        try:
            if int(lesson["id"]) == int(lesson_id):
                return lesson

        except Exception as e:
            log_error(e)
            return None
    return None

def import_file(self):
    try:
        from PySide6.QtWidgets import QFileDialog, QInputDialog
    except ModuleNotFoundError as me:
        log_error(me)
        print(me)
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
                lesson_data = decrypt_with_password(open(file_path, "rb").read(), password)
            except (FileNotFoundError, PermissionError, JSONDecodeError) as fe:
                log_error(fe)
                print(fe)
                return
        else:
            try:
                lesson_data = open(file_path, "rb").read().decode("utf-8")
            except (FileNotFoundError, PermissionError, JSONDecodeError) as fe:
                log_error(fe)
                print(fe)
                return
        merge_lessons(lesson_data)

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
            for lesson in new_lessons["lessons"]:
                lesson["id"] = len(lessons) + 1
                lessons.append(lesson)
        else:
            print("❌ Input must be a list/dict of lessons (a).")
            print(type(new_lessons))
            return None
    else:
        print("❌ Input must be a list/dict of lessons.")
        for lesson in new_lessons:
            lesson["id"] = len(lessons) + 1
            lessons.append(lesson)

    write_json(file_path, data)
    print(f"✅ Added {len(new_lessons)} lessons.")
    return "SUCCESS"

def write_save_data(host, port, ip_type, username_setting):
    full_path = get_appdata_path()
    with open(join(full_path, "connect-data.txt"), "wb") as f:
        data = f"{port}\n{ip_type}\n{host}"
        data = encrypt_file(data)
        f.write(data)

    with open(join(full_path, "username.dat"), "wb") as f:
        data = encrypt_file(str(username_setting))
        f.write(data)


def find_lesson(lesson_id):
    file_path = join(get_appdata_path(), "lessons.json")

    try:
        data = load_json(file_path)

    except (FileNotFoundError, JSONDecodeError) as fe:
        log_error(fe)
        print()
        makedirs(join(get_appdata_path(), "images"), exist_ok=True)
        write_data = {"lessons": []}
        write_json(file_path, write_data)
        return None

    for lesson in data["lessons"]:
        if int(lesson["id"]) == int(lesson_id):
            try:
                is_complete = str(lesson["completed"])

            except Exception as e:
                log_error(e)
                is_complete = "False"

            for quiz in lesson["quiz"]:  # Loop over the quiz list
                return (
                    str(lesson["id"]),
                    str(lesson["title"]),
                    str(lesson["image"]),
                    str(lesson["description"]),
                    str(lesson["content"]),
                    str(quiz["question"]),
                    str(quiz["answer"]),
                    str(is_complete),
                )
    return None
