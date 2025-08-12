from json import loads, dumps, JSONDecodeError
from os.path import join
from os import makedirs
from .paths import get_appdata_path
from .logger import log_error
from utils.crypto import decrypt_file, encrypt_file


def mark_lesson_finish(lesson_id):
    file_path = join(get_appdata_path(), "lessons.json")
    try:
        with open(file_path, "rb") as file:
            data = loads(decrypt_file(file.read()))

    except FileNotFoundError as fe:
        print(fe)
        print()
        makedirs(join(get_appdata_path(), "images"), exist_ok=True)

        with open(file_path, "wb") as file:
            data = {"lessons": []}
            file.write(encrypt_file(dumps(data)))
            return None

    except JSONDecodeError:
        with open(file_path, "wb") as file:
            data = {"lessons": []}
            file.write(encrypt_file(dumps(data)))

    for lesson in data["lessons"]:
        try:
            if int(lesson["id"]) == int(lesson_id):
                return lesson

        except Exception as e:
            print(e)
            return None


def find_lesson(lesson_id):
    file_path = join(get_appdata_path(), "lessons.json")

    try:
        with open(file_path, "rb") as file:
            data = loads(decrypt_file(file.read()))

    except FileNotFoundError as fe:
        log_error(fe)
        print()
        makedirs(join(get_appdata_path(), "images"), exist_ok=True)
        with open(file_path, "wb") as file:
            write_data = {"lessons": []}
            write_data = dumps(write_data)
            file.write(encrypt_file(write_data))
            return None

    except JSONDecodeError as je:
        with open(file_path, "wb") as file:
            write_data = {"lessons": []}
            write_data = dumps(write_data)
            file.write(encrypt_file(write_data))

        log_error(je)

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
