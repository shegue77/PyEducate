# Copyright (C) 2025 shegue77
# SPDX-License-Identifier: GPL-3.0-or-later
# DEPRECATED, USE server.py INSTEAD

# ------------------------------------------------------[ DEPENDENCIES ]-----------------------------------------------------
from sys import argv as sys_argv, exit as sys_exit
from json import loads, dumps, JSONDecodeError
from datetime import datetime
from os.path import join
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLineEdit,
    QLabel,
    QPushButton,
    QApplication,
    QVBoxLayout,
    QPlainTextEdit,
)
from PySide6.QtGui import Qt
from utils.server.paths import get_appdata_path
from utils.server.storage import list_lessons, find_lesson, load_json, write_json

# ----------------------------------------------------------------------------------------------------------------------------


def log_error(data):
    # Get current time
    now = datetime.now()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    log_path = join(get_appdata_path(), "lesson-editor.log")

    data = str(timestamp + " " + str(data) + "\n")

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(data)

    except FileNotFoundError:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(data)

    except PermissionError:
        print(f"[!] Insufficient permissions!\nUnable to log data at {log_path}!")


class Editor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyEducate: Lesson Editor")
        self.id_input = 1
        self.setContentsMargins(40, 40, 40, 40)
        self.initui()

    @staticmethod
    def create_json(id_input, all_texts):
        file_path = join(get_appdata_path(), "lessons.json")

        title = all_texts[0].text()
        mild_desc = str(all_texts[1].text())
        points = str(all_texts[2].text())
        content = str(all_texts[3].toPlainText().replace("\n", "\\n"))
        question = str(all_texts[4].text())
        answer = str(all_texts[5].toPlainText().replace("\n", "\\n"))
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
            return

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

    @staticmethod
    def edit_json(id_n):
        file_path = join(get_appdata_path(), "lessons.json")
        data = load_json(file_path)

        for lesson in data["lessons"]:
            if int(lesson["id"]) == int(id_n):
                correct_lesson = lesson
                title = correct_lesson["title"]
                image_path = correct_lesson["image"]
                description = correct_lesson["description"]
                content = correct_lesson["content"]

                try:
                    points = correct_lesson["points"]

                except Exception as e:
                    log_error(e)
                    points = "0"

                try:
                    for quiz in correct_lesson["quiz"]:  # Loop over the quiz list
                        options_text = str(quiz["question"])
                        answer = str(quiz["answer"])
                        return (
                            title,
                            image_path,
                            description,
                            content,
                            options_text,
                            answer,
                            points,
                        )

                except Exception as e:
                    log_error(e)
                    break

    def del_json(self):
        file_path = join(get_appdata_path(), "lessons.json")

        data = load_json(file_path)

        for lesson in data["lessons"]:
            for id_num in str(lesson["id"]):
                if id_num == str(self.id_input):
                    data["lessons"].remove(lesson)
                    write_json(file_path, data)
                    print(f"Lesson with ID {id_num} is being deleted...")

        existing_ids = []

        for lesson in data["lessons"]:
            for id_num in str(lesson["id"]):
                existing_ids.append(id_num)

        try:
            if int(self.id_input) not in existing_ids:
                self.status.setText(
                    f"✅ Lesson with ID {self.id_input} has been successfully deleted!"
                )
            else:
                self.status.setText(
                    f"❌ Lesson with ID {self.id_input} is unable to be removed!"
                )

        except Exception as e:
            log_error(e)

    def initui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title = QLabel("PyEducate: Lesson Maker/Editor\n\nDEPRECATED, USE server.py instead.", self)
        create = QPushButton("Create Lesson", self)
        edit = QPushButton("Edit Lesson", self)
        delete = QPushButton("Delete Lesson", self)
        list_l = QPushButton("List Lessons", self)
        lesson_info = QPushButton("Lesson Information", self)
        settings = QPushButton("Settings (Coming Soon)", self)
        settings.setDisabled(True)

        title.setObjectName("title")
        create.setObjectName("create")
        edit.setObjectName("edit")
        delete.setObjectName("delete")
        settings.setObjectName("settings")
        list_l.setObjectName("list_l")

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)
        layout.addWidget(create)
        layout.addWidget(edit)
        layout.addWidget(delete)
        layout.addWidget(list_l)
        layout.addWidget(lesson_info)
        layout.addWidget(settings)
        layout.addStretch(1)

        self.setStyleSheet(
            """
                    QMainWindow{
                        background-color: white;
                    }
                    QLabel{
                        color: black;
                    }
                    QLabel#title{
                        font-size: 40px;
                        font-weight: bold;
                        text-decoration: underline;
                    }
                    
                    QPushButton{
                        background-color: hsl(0, 1%, 27%);
                        color: white;
                        border: 1px solid;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 25px;
                    }
                    QPushButton:hover{
                        background-color: hsl(0, 1%, 47%);
                        color: white;
                        border: 1px solid;
                        border-radius: 5px;
                    }
                """
        )

        create.clicked.connect(self.initui_lesson)
        edit.clicked.connect(self.init_edit_prompt)
        delete.clicked.connect(self.init_del_menu)
        settings.clicked.connect(self.init_settings)
        list_l.clicked.connect(self.list_lessons_ui)
        lesson_info.clicked.connect(self.lesson_info_ui_dialog)

        central.setLayout(layout)

    def lesson_info_ui_dialog(self):
        def get_data():
            lesson_id = self.lesson_id_box.text()
            if len(lesson_id) != 0:
                try:
                    int(lesson_id)
                except (ValueError, TypeError) as ve:
                    print(ve)
                    log_error(ve)
                    return

                data = find_lesson(lesson_id)
                if data is not None:
                    self.list_lesson_ui(data)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title = QLabel("PyEducate: Lesson Info", self)
        self.lesson_id_box = QLineEdit(self)
        self.lesson_id_box.setPlaceholderText("Enter Lesson ID")
        submit = QPushButton("Get Lesson Info", self)

        go_back = QPushButton("Go Back", self)

        title.setObjectName("title")

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.lesson_id_box)
        layout.addWidget(submit)
        layout.addSpacing(1)
        layout.addWidget(go_back)

        self.setStyleSheet(
            """
                                    QMainWindow{
                                        background-color: white;
                                    }
                                    QLabel{
                                        color: black;
                                        font-size: 25px;
                                    }
                                    QLabel#title{
                                        font-size: 40px;
                                        font-weight: bold;
                                    }
                                    QLineEdit{
                                        background-color: white;
                                        color: black;
                                        border: 1px solid;
                                        border-radius: 5px;
                                        font-size: 20px;
                                    }
                                    QPushButton{
                                        background-color: hsl(0, 1%, 27%);
                                        color: white;
                                        border: 1px solid;
                                        border-radius: 5px;
                                        font-weight: bold;
                                        font-size: 25px;
                                    }
                                    QPushButton:hover{
                                        background-color: hsl(0, 1%, 47%);
                                        color: white;
                                        border: 1px solid;
                                        border-radius: 5px;
                                    }
                                """
        )

        central.setLayout(layout)

        submit.clicked.connect(get_data)
        go_back.clicked.connect(self.initui)

    def list_lesson_ui(self, data):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        lesson_order = (
            "ID:",
            "title",
            "Image:",
            "Description:",
            "Content:",
            "Quiz Question:",
            "Quiz Answer:",
        )

        title = QLabel(self)
        title.setText(str(data[1]))

        lesson_data = ""
        for idx, part in enumerate(lesson_order):
            if idx != 1:
                lesson_data += f"{part} {str(data[idx])}\n"
            else:
                continue

        info_label = QLabel(self)
        info_label.setText(str(lesson_data))

        go_back = QPushButton("Go Back", self)
        title.setObjectName("title")

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(info_label)
        layout.addWidget(go_back)

        self.setStyleSheet(
            """
                                    QMainWindow{
                                        background-color: white;
                                    }
                                    QLabel{
                                        color: black;
                                    }
                                    QLabel#title{
                                        font-size: 30px;
                                        font-weight: bold;
                                    }
                                    QLineEdit{
                                        background-color: white;
                                        color: black;
                                        border: 1px solid;
                                        border-radius: 5px;
                                        font-size: 20px;
                                    }
                                    QPushButton{
                                        background-color: hsl(0, 1%, 27%);
                                        color: white;
                                        border: 1px solid;
                                        border-radius: 5px;
                                        font-weight: bold;
                                        font-size: 25px;
                                    }
                                    QPushButton:hover{
                                        background-color: hsl(0, 1%, 47%);
                                        color: white;
                                        border: 1px solid;
                                        border-radius: 5px;
                                    }
                                """
        )

        central.setLayout(layout)

        go_back.clicked.connect(self.initui)

    def list_lessons_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        data = list_lessons()

        title = QLabel("PyEducate: Lesson List", self)
        lessons = QLabel(self)
        lessons.setText(data.replace("\\n", "\n"))
        go_back = QPushButton("Go Back", self)

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(lessons)
        layout.addWidget(go_back)

        title.setObjectName("title")

        self.setStyleSheet(
            """
                            QMainWindow{
                                background-color: white;
                            }
                            QLabel{
                                color: black;
                            }
                            QLabel#title{
                                font-size: 30px;
                                font-weight: bold;
                            }

                            QPushButton{
                                background-color: hsl(0, 1%, 27%);
                                color: white;
                                border: 1px solid;
                                border-radius: 5px;
                                font-weight: bold;
                                font-size: 25px;
                            }
                            QPushButton:hover{
                                background-color: hsl(0, 1%, 47%);
                                color: white;
                                border: 1px solid;
                                border-radius: 5px;
                            }
                        """
        )

        central.setLayout(layout)
        go_back.clicked.connect(self.initui)

    def initui_lesson(self):
        def add_json():
            all_texts = (
                self.title_name,
                self.description_text,
                self.point_amount,
                self.content_text,
                self.quiz_question_text,
                self.quiz_answer_text,
                self.image_path,
            )
            required_texts = [
                self.title_name.text(),
                self.description_text.text(),
                self.content_text.toPlainText(),
                self.quiz_question_text.text(),
                self.quiz_answer_text.toPlainText(),
            ]
            for text in required_texts:
                if str(text) == "":
                    return

            for part in all_texts:
                try:
                    part.setText(str(part.text()).replace('"', "'"))

                except AttributeError:
                    part.setPlainText(str(part.toPlainText()).replace('"', "'"))

            self.id_input = self.create_json(self.id_input, all_texts)
            self.initui()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title_title = QLabel("PyEducate: Lesson Maker", self)

        self.title_name = QLineEdit(self)
        self.title_name.setPlaceholderText("Enter Title (Required)")

        self.image_path = QLineEdit(self)
        self.image_path.setPlaceholderText("Enter Image Path (Work in progress)")
        self.image_path.setDisabled(True)

        self.point_amount = QLineEdit(self)
        self.point_amount.setPlaceholderText(
            "Enter amount of points (Optional, given to user based on attempts)"
        )

        self.description_text = QLineEdit(self)
        self.description_text.setPlaceholderText(
            "Subtitle/Quick Description (Required)"
        )

        self.content_text = QPlainTextEdit(self)
        self.content_text.setPlaceholderText(
            "Full description (Required, Can be Multi-line)"
        )

        self.quiz_question_text = QLineEdit(self)
        self.quiz_question_text.setPlaceholderText(
            "Quiz Question (Required, one question only)"
        )

        self.quiz_answer_text = QPlainTextEdit(self)
        self.quiz_answer_text.setPlaceholderText(
            "Quiz Answer (Required, ensure valid syntax)"
        )

        submit_data = QPushButton("Submit", self)
        go_back_del = QPushButton("Main Menu")

        layout.addWidget(title_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.title_name)
        layout.addWidget(self.image_path)
        layout.addWidget(self.point_amount)
        layout.addWidget(self.description_text)
        layout.addWidget(self.content_text)
        layout.addWidget(self.quiz_question_text)
        layout.addWidget(self.quiz_answer_text)
        layout.addWidget(submit_data)
        layout.addWidget(go_back_del)

        title_title.setObjectName("title_title")

        self.setStyleSheet(
            """
                            QMainWindow{
                                background-color: white;
                            }
                            QLabel{
                                color: black;
                            }
                            QLabel#title_title{
                                font-size: 30px;
                                font-weight: bold;
                            }
                            QLineEdit{
                                background-color: white;
                                color: black;
                                border: 1px solid;
                                border-radius: 5px;
                            }
                            QPlainTextEdit{
                                background-color: white;
                                color: black;
                                border: 1px solid;
                                border-radius: 5px;
                            }
                            QPushButton{
                                background-color: hsl(0, 1%, 27%);
                                color: white;
                                border: 1px solid;
                                border-radius: 5px;
                                font-weight: bold;
                                font-size: 25px;
                            }
                            QPushButton:hover{
                                background-color: hsl(0, 1%, 47%);
                                color: white;
                                border: 1px solid;
                                border-radius: 5px;
                            }
                        """
        )

        go_back_del.clicked.connect(self.initui)
        submit_data.clicked.connect(add_json)

        central.setLayout(layout)

    def init_edit_prompt(self):
        file_path = join(get_appdata_path(), "lessons.json")

        def _submit():
            is_valid_id = False
            try:
                data = load_json(file_path)

                for lesson in data["lessons"]:
                    if str(lesson["id"]) == str(self.id_name.text()):
                        is_valid_id = True
                        break

            except FileNotFoundError as fe:
                log_error(fe)
                return

            if is_valid_id:
                self.init_edit_menu(self.id_name.text())

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title_title = QLabel("Enter Lesson ID", self)
        self.id_name = QLineEdit(self)
        self.id_name.setPlaceholderText("Enter ID")

        submit_data = QPushButton("Submit Data", self)
        go_back_edit = QPushButton("Main Menu", self)

        layout.addWidget(title_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.id_name)
        layout.addWidget(submit_data)
        layout.addWidget(go_back_edit)

        title_title.setObjectName("title")

        self.setStyleSheet(
            """
                            QMainWindow{
                                background-color: white;
                            }
                            QLabel{
                                color: black;
                            }
                            QLabel#title{
                                font-size: 30px;
                                font-weight: bold;
                            }
                            QLineEdit{
                                background-color: white;
                                color: black;
                                border: 1px solid;
                                border-radius: 5px;
                                font-size: 20px;
                            }
                            QPushButton{
                                background-color: hsl(0, 1%, 27%);
                                color: white;
                                border: 1px solid;
                                border-radius: 5px;
                                font-weight: bold;
                                font-size: 25px;
                            }
                            QPushButton:hover{
                                background-color: hsl(0, 1%, 47%);
                                color: white;
                                border: 1px solid;
                                border-radius: 5px;
                            }
                        """
        )

        submit_data.clicked.connect(_submit)
        go_back_edit.clicked.connect(self.initui)
        central.setLayout(layout)

    def edit_file(self):
        self.del_json()
        all_texts = (
            self.title_name,
            self.description_text,
            self.point_amount,
            self.content_text,
            self.quiz_question_text,
            self.quiz_answer_text,
            self.image_path,
        )
        self.id_input = self.create_json(self.id_input, all_texts)
        self.initui()

    def init_edit_menu(self, id_n="0"):
        self.id_input = id_n

        text = self.edit_json(id_n)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title_title = QLabel("PyEducate: Lesson Editor", self)

        self.title_name = QLineEdit(self)
        self.title_name.setPlaceholderText("Edit Title")
        self.title_name.setText(str(text[0]))

        self.image_path = QLineEdit(self)
        self.image_path.setPlaceholderText("Edit Image Path (Coming Soon)")
        self.image_path.setText(str(text[1]))
        self.image_path.setDisabled(True)

        self.description_text = QLineEdit(self)
        self.description_text.setPlaceholderText("Edit Quick Description")
        self.description_text.setText(str(text[2]))

        self.content_text = QPlainTextEdit(self)
        self.content_text.setPlaceholderText(
            "Edit full description and answers (Can be Multi-line)"
        )
        self.content_text.setPlainText(str(text[3]))

        self.quiz_question_text = QLineEdit(self)
        self.quiz_question_text.setPlaceholderText(
            "Edit Quiz Question (One question only)"
        )
        self.quiz_question_text.setText(str(text[4]))

        self.quiz_answer_text = QPlainTextEdit(self)
        self.quiz_answer_text.setPlainText(str(text[5]))

        self.point_amount = QLineEdit(self)
        self.point_amount.setPlaceholderText("Edit max points")
        self.point_amount.setText(str(text[6]))

        submit_data = QPushButton("Submit Data", self)
        go_back_edit = QPushButton("Main Menu", self)

        layout.addWidget(title_title)
        layout.addWidget(self.title_name)
        layout.addWidget(self.image_path)
        layout.addWidget(self.point_amount)
        layout.addWidget(self.description_text)
        layout.addWidget(self.content_text)
        layout.addWidget(self.quiz_question_text)
        layout.addWidget(self.quiz_answer_text)
        layout.addWidget(submit_data)
        layout.addWidget(go_back_edit)

        title_title.setObjectName("title_title")

        self.setStyleSheet(
            """
                                    QMainWindow{
                                        background-color: white;
                                    }
                                    QLabel{
                                        color: black;
                                    }
                                    QLabel#title_title{
                                        font-size: 30px;
                                        font-weight: bold;
                                    }
                                    QLineEdit{
                                        background-color: white;
                                        color: black;
                                        border: 1px solid;
                                        border-radius: 5px;
                                    }
                                    QPlainTextEdit{
                                        background-color: white;
                                        color: black;
                                        border: 1px solid;
                                        border-radius: 5px;
                                    }
                                    QPushButton{
                                        background-color: hsl(0, 1%, 27%);
                                        color: white;
                                        border: 1px solid;
                                        border-radius: 5px;
                                        font-weight: bold;
                                        font-size: 25px;
                                    }
                                    QPushButton:hover{
                                        background-color: hsl(0, 1%, 47%);
                                        color: white;
                                        border: 1px solid;
                                        border-radius: 5px;
                                    }
                                """
        )

        go_back_edit.clicked.connect(self.initui)
        submit_data.clicked.connect(self.edit_file)

        central.setLayout(layout)

    def init_del_menu(self):
        def _submit():
            self.id_input = self.id_input_data.text()
            self.del_json()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title = QLabel("PyEducate: Lesson Editor", self)
        self.id_input_data = QLineEdit(self)
        self.id_input_data.setPlaceholderText("Enter Lesson ID")
        delete_button = QPushButton("Delete Selected Lesson", self)
        self.status = QLabel("", self)
        go_back_del = QPushButton("Main Menu")

        delete_button.clicked.connect(_submit)
        go_back_del.clicked.connect(self.initui)

        title.setObjectName("title")

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.id_input_data)
        layout.addWidget(self.status)
        layout.addWidget(delete_button)
        layout.addWidget(go_back_del)

        self.setStyleSheet(
            """
                            QMainWindow{
                                background-color: white;
                            }
                            QLabel{
                                color: black;
                            }
                            QLabel#title{
                                font-size: 30px;
                                font-weight: bold;
                            }
                            QLineEdit{
                                background-color: white;
                                color: black;
                                border: 1px solid;
                                border-radius: 5px;
                                font-size: 25px;
                            }
                            QPushButton{
                                background-color: hsl(0, 1%, 27%);
                                color: white;
                                border: 1px solid;
                                border-radius: 5px;
                                font-weight: bold;
                                font-size: 25px;
                            }
                            QPushButton:hover{
                                background-color: hsl(0, 1%, 47%);
                                color: white;
                                border: 1px solid;
                                border-radius: 5px;
                            }
                        """
        )

        central.setLayout(layout)

    def init_settings(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title = QLabel("Settings", self)
        file_save = QLineEdit(self)
        file_save.setPlaceholderText("File Save Path")
        file_save.setText("%APPDATA%")
        file_save.setDisabled(True)
        go_back = QPushButton("Go Back", self)

        title.setObjectName("title")

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(file_save)
        layout.addWidget(go_back)
        go_back.clicked.connect(self.initui)

        self.setStyleSheet(
            """
                            QMainWindow{
                                background-color: white;
                            }
                            QLabel{
                                color: black;
                            }
                            QLabel#title{
                                font-size: 30px;
                                font-weight: bold;
                            }
                            QLineEdit{
                                background-color: hsl(4, 0%, 51%);
                                color: black;
                                border: 1px solid;
                                border-radius: 5px;
                                font-size: 25px;
                            }
                            QPushButton{
                                background-color: hsl(0, 1%, 27%);
                                color: white;
                                border: 1px solid;
                                border-radius: 5px;
                                font-weight: bold;
                                font-size: 25px;
                            }
                            QPushButton:hover{
                                background-color: hsl(0, 1%, 47%);
                                color: white;
                                border: 1px solid;
                                border-radius: 5px;
                            }
                        """
        )

        central.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys_argv)
    window = Editor()
    window.show()
    sys_exit(app.exec())
