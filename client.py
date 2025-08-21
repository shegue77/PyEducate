# Copyright (C) 2025 shegue77
# SPDX-License-Identifier: GPL-3.0-or-later

# ---------------------------[ DEPENDENCIES ]---------------------------
from sys import argv as sys_argv, exit as sys_exit
from json import loads, dumps, JSONDecodeError
from threading import Thread
from time import sleep
from os import makedirs
from os.path import exists as os_path_exists, join
from datetime import datetime
from network.client import connectmod
from utils.client.paths import get_appdata_path
from utils.crypto import encrypt_file, decrypt_file
from utils.client.storage import find_lesson, mark_lesson_finish, write_json, load_json

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QMessageBox,
    QStyle,
    QSizePolicy,
)
from PySide6.QtGui import Qt
from PySide6.QtCore import QSize


# ----------------------------------------------------------------------


def log_error(data):
    # Get current time
    now = datetime.now()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    log_path = str(join(get_appdata_path(), "client.log"))

    data = str(timestamp + " " + str(data) + "\n")

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(data)

    except FileNotFoundError:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(data)

    except PermissionError:
        print(f"[!] Insufficient permissions!\nUnable to log data at {log_path}!")


def disconnect():
    connectmod.close_client()


def attempt_connect_loop(server_ip, server_port, ip_type):
    while True:
        try:
            connectmod.start_client(server_ip, server_port, ip_type)
            break
        except (ConnectionError, ConnectionRefusedError, ConnectionResetError) as e:
            try:
                connectmod.close_client()

            except Exception:
                pass
            print(f"{e} Retrying in 10 seconds...")
            sleep(10)


try:
    with open(join(get_appdata_path(), "connect-data.txt"), "rb") as f:
        data = decrypt_file(f.read()).strip().split()
        SERVER_IP = str(data[0])
        SERVER_PORT = int(data[1])
        IP_TYPE = str(data[2])

    Thread(
        target=attempt_connect_loop, args=(SERVER_IP, SERVER_PORT, IP_TYPE), daemon=True
    ).start()

except FileNotFoundError as fe:
    print(f"[!!] Connect data not found!\n{fe}")

except (ValueError, TypeError, IndexError) as ve:
    print(f"[!!] Corrupted data!\n{ve}")
    file_path = join(get_appdata_path(), "connect-data.txt")
    with open(file_path, "wb") as file:
        file.write(encrypt_file(""))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyEducate: School Edition")
        self.setContentsMargins(20, 20, 20, 20)
        self.data = None
        self.page = 1
        self.points = 0.0
        self.lessons_completed = 0
        self.lesson_attempt = 1
        self.leaderboard_page = 1
        self.leaderboard_type = "points"

        self.reload_json()
        self.search()

    def closeEvent(self, event):
        try:
            connectmod.close_client()
        except Exception:
            pass
        event.accept()

    def save_data(self):
        file_path = str(join(get_appdata_path(), "SAVE_DATA.dat"))
        with open(file_path, "wb") as file:
            write_data = f"{str(self.points)} {str(self.lessons_completed)}"
            file.write(encrypt_file(write_data))
        print("Point data saved successfully")

    def show_message_box(self, mode, title, text):

        if mode == "warning":
            msg_box = QMessageBox()
            msg_box.setWindowTitle(str(title))
            msg_box.setText(str(text))
            msg_box.setContentsMargins(20, 20, 20, 20)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.setStyleSheet(
                """
                        QWidget{
                            background-color: white;
                        }
                        QLabel{
                            color: black;
                        }
                        QPushButton{
                            font-size: 20px;
                            border: 2px solid;
                            border-radius: 5px;
                            color: black;
                            font-weight: bold;
                        }
                    """
            )

            msg_box.exec()

        elif mode == "error":
            msg_box = QMessageBox()
            msg_box.setWindowTitle(str(title))
            msg_box.setText(str(text))
            msg_box.setContentsMargins(20, 20, 20, 20)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.setStyleSheet(
                """
                                    QWidget{
                                        background-color: white;
                                    }
                                    QLabel{
                                        color: black;
                                    }
                                    QPushButton{
                                        font-size: 20px;
                                        border: 2px solid;
                                        border-radius: 5px;
                                        color: black;
                                        font-weight: bold;
                                    }
                                """
            )

            msg_box.exec()

        elif mode == "info":
            msg_box = QMessageBox()
            msg_box.setWindowTitle(str(title))
            msg_box.setText(str(text))
            msg_box.setContentsMargins(20, 20, 20, 20)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.setStyleSheet(
                """
                                    QWidget{
                                        background-color: white;
                                    }
                                    QLabel{
                                        color: black;
                                    }
                                    QPushButton{
                                        font-size: 20px;
                                        border: 2px solid;
                                        border-radius: 5px;
                                        color: black;
                                        font-weight: bold;
                                    }
                                """
            )

            msg_box.exec()

    def reload_json(self):
        file_path = join(get_appdata_path(), "lessons.json")
        try:
            self.data = load_json(file_path)
            print("reloaded lessons.json")

        except FileNotFoundError as fe:
            log_error(fe)
            print(fe)
            print()
            makedirs(join(get_appdata_path(), "images"), exist_ok=True)
            write_data = {"lessons": []}
            write_json(file_path, write_data)
            print("reloaded")

        except JSONDecodeError:
            write_data = {"lessons": []}
            write_json(file_path, write_data)
            print("reloaded")

    def submit_id_data(self, id_n):

        status = "Fail"
        file_path = join(get_appdata_path(), "lessons.json")
        for lesson in self.data["lessons"]:
            if int(lesson["id"]) == int(id_n):
                correct_lesson = lesson
                status = "Success"
                break

            try:
                self.data = load_json(file_path)

            except FileNotFoundError as fe:
                log_error(fe)
                print(fe)
                print()
                makedirs(join(get_appdata_path(), "images"), exist_ok=True)
                write_data = {"lessons": []}
                write_json(file_path, write_data)

            except Exception as e:
                self.data = load_json(file_path)
                print(e)
                break

        if status == "Success":
            self.init_lesson(correct_lesson)
        else:
            try:
                with open(file_path, "rb") as file:
                    self.data = loads(decrypt_file(file.read()))
                    print("reloaded")

            except FileNotFoundError as fe:
                log_error(fe)
                print(fe)
                print()
                makedirs(join(get_appdata_path(), "images"), exist_ok=True)
                if not os_path_exists(file_path):
                    with open(file_path, "wb") as file:
                        write_data = {"lessons": []}
                        write_data = dumps(write_data)
                        file.write(encrypt_file(write_data))

            except JSONDecodeError:
                with open(file_path, "wb") as file:
                    write_data = {"lessons": []}
                    write_data = dumps(write_data)
                    file.write(encrypt_file(write_data))

    @staticmethod
    def get_lessons_for_page(page_number):
        file_path = join(get_appdata_path(), "lessons.json")
        try:
            data = load_json(file_path)

        except FileNotFoundError as fe:
            log_error(fe)
            print(fe)
            print()
            makedirs(join(get_appdata_path(), "images"), exist_ok=True)
            write_data = {"lessons": []}
            write_json(file_path, write_data)
            return []

        except JSONDecodeError as je:
            log_error(je)

            write_data = {"lessons": []}
            write_json(file_path, write_data)
            return []

        items_per_page = 8
        start_index = (page_number - 1) * items_per_page
        end_index = start_index + items_per_page
        ids = []
        try:
            for lesson in data["lessons"][start_index:end_index]:
                ids.append(lesson["id"])

        except IndexError as ie:
            log_error(ie)
            return [None]

        return ids

    @staticmethod
    def list_lesson_ids():
        file_path = join(get_appdata_path(), "lessons.json")

        def create_json():
            data = {"lessons": []}
            write_json(file_path, data)

        try:
            data = load_json(file_path)

        except FileNotFoundError as fe:
            log_error(fe)
            print(fe)
            print()
            create_json()
            return 1

        except JSONDecodeError:
            data = {"lessons": []}
            write_json(file_path, data)

        whole_data = []
        pages = (len(data["lessons"]) + 8 - 1) // 8
        for lesson in data["lessons"]:
            whole_data.append(int(lesson["id"]))

        return pages

    def search(self):
        save_data_path = join(get_appdata_path(), "SAVE_DATA.dat")
        try:
            with open(save_data_path, "rb") as f:
                save_data = decrypt_file(f.read()).strip().split()
                self.points = float(save_data[0])
                self.lessons_completed = int(save_data[1])

        except FileNotFoundError as fe:
            log_error(fe)
            with open(save_data_path, "wb") as f:
                f.write(encrypt_file("0 0"))

        except IndexError as ie:
            self.points = 0.0
            self.lessons_completed = 0
            log_error(ie)

        def reload_ui():
            self.search()
            self.show_message_box(
                "info", "Lesson Reload", "Successfully reloaded lessons."
            )

        central = QWidget()
        self.setCentralWidget(central)
        total_pages = self.list_lesson_ids()

        def setup_page():
            pages_lessons = self.get_lessons_for_page(self.page)

            if any(pages_lessons):
                return pages_lessons

            if self.page != 1:
                print(f"[!] No lesson IDs on page {self.page}.")
                self.page = 1
                return None

            return [None, None, None, None, None, None, None, None]

        while True:
            result = setup_page()
            if result is not None:
                passed_lessons = result
                break

        def next_page_set(total_page: int):
            if self.page >= total_page:
                return None

            self.page += 1
            self.search()

        def previous_page_set():
            if self.page <= 1:
                return None

            self.page -= 1
            self.search()

        all_layouts = QVBoxLayout(self)
        top_layout = QVBoxLayout(self)
        second_top_layout = QHBoxLayout(self)
        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout(self)
        second_left_layout = QVBoxLayout(self)
        second_right_layout = QVBoxLayout(self)
        right_layout = QVBoxLayout(self)
        page_layout = QHBoxLayout(self)
        bottom_layout = QVBoxLayout(self)

        title_label = QLabel("PyEducate", self)
        title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        top_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        reload_lessons = QPushButton("Reload lessons 🔄️", self)
        second_top_layout.addWidget(reload_lessons)

        show_leaderboard = QPushButton("Leaderboard 🏆", self)
        second_top_layout.addWidget(show_leaderboard)

        while True:
            if len(passed_lessons) < 8:
                passed_lessons.append(None)
            else:
                break

        button_1 = QPushButton(self)
        button_2 = QPushButton(self)
        button_3 = QPushButton(self)
        button_4 = QPushButton(self)
        button_5 = QPushButton(self)
        button_6 = QPushButton(self)
        button_7 = QPushButton(self)
        button_8 = QPushButton(self)

        buttons = (
            button_1,
            button_2,
            button_3,
            button_4,
            button_5,
            button_6,
            button_7,
            button_8,
        )

        for idx, lesson in enumerate(passed_lessons):

            if lesson is not None:
                data = find_lesson(lesson)
                try:
                    text = QLabel(
                        f"{data[1]}\n{data[3]}\nID: {data[0]}\nCompleted: {data[7]}"
                    )

                except IndexError as te:
                    log_error(te)
                    print(te)
                    return None

                text.setWordWrap(True)

            else:
                text = QLabel(
                    "Placeholder\nUnknown Description\nID: ??\nCompleted: N/A"
                )
                data = ""

            if idx in (0, 1):
                left_layout.addWidget(text)
                if passed_lessons[idx] is None or data[7] == "True":
                    buttons[idx].setText("Lesson complete")
                    buttons[idx].setDisabled(True)
                else:
                    buttons[idx].setText("Start lesson")
                    buttons[idx].setDisabled(False)

                left_layout.addWidget(buttons[idx])

            elif idx in (2, 3):
                second_left_layout.addWidget(text)
                if passed_lessons[idx] is None or data[7] == "True":
                    buttons[idx].setText("Lesson complete")
                    buttons[idx].setDisabled(True)
                else:
                    buttons[idx].setText("Start lesson")
                    buttons[idx].setDisabled(False)

                second_left_layout.addWidget(buttons[idx])

            elif idx in (4, 5):
                right_layout.addWidget(text)
                if passed_lessons[idx] is None or data[7] == "True":
                    buttons[idx].setText("Lesson complete")
                    buttons[idx].setDisabled(True)
                else:
                    buttons[idx].setText("Start lesson")
                    buttons[idx].setDisabled(False)

                right_layout.addWidget(buttons[idx])

            elif idx in (6, 7):
                second_right_layout.addWidget(text)
                if passed_lessons[idx] is None or data[7] == "True":
                    buttons[idx].setText("Lesson complete")
                    buttons[idx].setDisabled(True)
                else:
                    buttons[idx].setText("Start lesson")
                    buttons[idx].setDisabled(False)

                second_right_layout.addWidget(buttons[idx])

        if total_pages is None or total_pages == 0:
            total_pages = 1

        total_pages_text = QLabel(f"Page: {self.page}/{total_pages}", self)
        total_pages_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        bottom_layout.addWidget(total_pages_text, stretch=1)

        previous_page = QPushButton(self)

        next_page = QPushButton(self)

        settings = QPushButton("⚙️ Settings", self)
        bottom_layout.addWidget(settings)

        icon_size = QSize(48, 48)

        left_icon = self.style().standardIcon(QStyle.SP_ArrowLeft)
        previous_page.setIcon(left_icon)

        right_icon = self.style().standardIcon(QStyle.SP_ArrowRight)
        next_page.setIcon(right_icon)

        previous_page.setIconSize(icon_size)
        next_page.setIconSize(icon_size)

        page_layout.addWidget(previous_page)
        page_layout.addWidget(next_page)

        if self.page >= total_pages:
            next_page.setDisabled(True)
        else:
            next_page.setDisabled(False)

        if self.page <= 1:
            previous_page.setDisabled(True)
        else:
            previous_page.setDisabled(False)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(second_left_layout)
        main_layout.addLayout(right_layout)
        main_layout.addLayout(second_right_layout)

        all_layouts.addLayout(top_layout)
        all_layouts.addLayout(second_top_layout)
        all_layouts.addLayout(main_layout)
        all_layouts.addLayout(page_layout)
        all_layouts.addLayout(bottom_layout)

        title_label.setObjectName("title")

        self.setStyleSheet(
            """
                    QMainWindow{
                        background-color: white;
                    }
                    QWidget#central_widget{
                        border: 2px solid;
                        border-radius: 5px;
                    }
                    QLabel{
                        color: black;
                        font-weight: bold;
                        border: 2px solid;
                        border-radius: 5px;
                        font-size: 15px;
                    }
                    QLabel#title{
                        font-size: 45px;
                        border: None;
                        text-decoration: underline;
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

        central.setLayout(all_layouts)

        if passed_lessons[0] is not None:
            button_1.clicked.connect(lambda: self.submit_id_data(passed_lessons[0]))
        if passed_lessons[1] is not None:
            button_2.clicked.connect(lambda: self.submit_id_data(passed_lessons[1]))
        if passed_lessons[2] is not None:
            button_3.clicked.connect(lambda: self.submit_id_data(passed_lessons[2]))
        if passed_lessons[3] is not None:
            button_4.clicked.connect(lambda: self.submit_id_data(passed_lessons[3]))
        if passed_lessons[4] is not None:
            button_5.clicked.connect(lambda: self.submit_id_data(passed_lessons[4]))
        if passed_lessons[5] is not None:
            button_6.clicked.connect(lambda: self.submit_id_data(passed_lessons[5]))
        if passed_lessons[6] is not None:
            button_7.clicked.connect(lambda: self.submit_id_data(passed_lessons[6]))
        if passed_lessons[7] is not None:
            button_8.clicked.connect(lambda: self.submit_id_data(passed_lessons[7]))

        previous_page.clicked.connect(previous_page_set)
        next_page.clicked.connect(lambda: next_page_set(total_pages))
        reload_lessons.clicked.connect(reload_ui)
        settings.clicked.connect(self.init_settings)
        show_leaderboard.clicked.connect(self.init_leaderboard)

    def init_leaderboard(self):
        def read_leaderboard(filename):
            if not os_path_exists(filename):
                # Create empty file if it doesn't exist
                with open(filename, "wb") as file:
                    file.write(encrypt_file(dumps([])))
                return []

            with open(filename, "rb") as file:
                try:
                    json_data = loads(decrypt_file(file.read()))
                    return json_data
                except Exception as e:
                    log_error(e)
                    return []

        def get_top_n_users(filename, type_n="points", n=10):
            leaderboard = read_leaderboard(filename)
            # Sort by points descending
            sorted_leaderboard = sorted(
                leaderboard, key=lambda x: x[type_n], reverse=True
            )
            return sorted_leaderboard[:n]

        def get_total_pages():
            file_path = join(get_appdata_path(), "leaderboards.json")

            def create_json():
                with open(file_path, "wb") as f:
                    json_data = []
                    f.write(encrypt_file(dumps(json_data)))

            try:
                with open(file_path, "rb") as f:
                    data = loads(decrypt_file(f.read()))

            except FileNotFoundError as fe:
                log_error(fe)
                create_json()
                data = []

            except JSONDecodeError as je:
                log_error(je)
                with open(file_path, "wb") as file:
                    data = []
                    file.write(encrypt_file(data))

            leaderboard_items = []

            for part in data:
                for i in part.keys():
                    if i != "username":
                        leaderboard_items.append(i)
                break

            return leaderboard_items, len(leaderboard_items)

        def next_page_set(total_page: int):
            if self.leaderboard_page >= total_page:
                return None

            self.leaderboard_page += 1
            self.init_leaderboard()

        def previous_page_set():
            if self.leaderboard_page <= 1:
                return None

            self.leaderboard_page -= 1
            self.init_leaderboard()

        def get_board_type():
            board_types = get_total_pages()[0]
            try:
                self.leaderboard_type = str(board_types[self.leaderboard_page - 1])
            except IndexError as ie:
                log_error(ie)
                print(ie)
                self.show_message_box(
                    "error",
                    "Leaderboard",
                    "Unable to initialise the leaderboard!\n"
                    "This is due to no known players being on the leaderboard.",
                )
                return "Error"

        total_pages = int(get_total_pages()[1])
        status = get_board_type()
        if status == "Error":
            return None

        badge_for_ranking = {
            1: "🏆",
            2: "🥇",
            3: "🥈",
            4: "🥉",
            5: "🎖️",
        }

        all_layouts = QVBoxLayout()
        title_layout = QVBoxLayout()
        layout = QVBoxLayout()
        bottom_layout = QVBoxLayout()
        arrow_layout = QHBoxLayout()
        central = QWidget()
        self.setCentralWidget(central)

        title = QLabel("Leaderboard 🏆")
        title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        title_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        subtitle = QLabel(
            f"Top 10 by {str(self.leaderboard_type).replace('_', ' ').lower().capitalize()}"
        )
        subtitle.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        title_layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignHCenter)

        data = get_top_n_users(
            join(get_appdata_path(), "leaderboards.json"),
            str(self.leaderboard_type),
            10,
        )

        for idx, part in enumerate(data, start=1):
            try:
                badge = badge_for_ranking[idx]
            except IndexError:
                badge = ""

            person = QLabel(
                f'{badge} {idx}. Username: {part["username"]}  |  '
                f"{str(self.leaderboard_type).strip().replace('_', ' ').lower().capitalize()}: "
                f"{part[str(self.leaderboard_type.strip())]:,.2f}"
            )
            layout.addWidget(person)

        total_pages_text = QLabel(f"Page: {self.leaderboard_page}/{total_pages}", self)
        total_pages_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        bottom_layout.addWidget(total_pages_text, stretch=1)

        previous_page = QPushButton()
        next_page = QPushButton()

        icon_size = QSize(48, 48)

        left_icon = self.style().standardIcon(QStyle.SP_ArrowLeft)
        previous_page.setIcon(left_icon)

        right_icon = self.style().standardIcon(QStyle.SP_ArrowRight)
        next_page.setIcon(right_icon)

        previous_page.setIconSize(icon_size)
        next_page.setIconSize(icon_size)

        go_back = QPushButton("Go Back ↩️")
        bottom_layout.addWidget(go_back)

        arrow_layout.addWidget(previous_page)
        arrow_layout.addWidget(next_page)

        all_layouts.addLayout(title_layout)
        all_layouts.addLayout(layout)
        all_layouts.addLayout(arrow_layout)
        all_layouts.addLayout(bottom_layout)

        central.setLayout(all_layouts)

        if self.leaderboard_page >= total_pages:
            next_page.setDisabled(True)
        else:
            next_page.setDisabled(False)

        if self.leaderboard_page <= 1:
            previous_page.setDisabled(True)
        else:
            previous_page.setDisabled(False)

        title.setObjectName("title")
        subtitle.setObjectName("subtitle")

        self.setStyleSheet(
            """
                            QMainWindow{
                                background-color: white;
                            }
                            QWidget#central_widget{
                                border: 2px solid;
                                border-radius: 5px;
                            }
                            QLabel{
                                color: black;
                                font-weight: bold;
                                border: None;
                                border-radius: 5px;
                                font-size: 15px;
                                background-color: hsl(0, 1%, 87%);
                            }
                            QLabel#title{
                                font-size: 45px;
                                border: None;
                                text-decoration: underline;
                                font-weight: bold;
                                background-color: white;
                            }
                            QLabel#subtitle{
                                font-size: 20px;
                                border: None;
                                background-color: white;
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

        previous_page.clicked.connect(previous_page_set)
        next_page.clicked.connect(lambda: next_page_set(total_pages))
        go_back.clicked.connect(self.search)

    def init_lesson(self, lesson):
        def _submit_lesson():
            try:
                self.press_button(int(lesson["id"]), float(lesson["points"]))

            except Exception as e:
                log_error(e)
                self.press_button(int(lesson["id"]))

        options_text = ""
        for quiz in lesson["quiz"]:  # Loop over the quiz list
            options_text = quiz["question"]
            self.answer = str(quiz["answer"])

        central = QWidget()
        self.setCentralWidget(central)

        title = QLabel(str(lesson["title"]), self)
        desc = QLabel(str(lesson["description"]), self)

        content = QLabel(str(lesson["content"]).replace("\\n", "\n"), self)
        content.setWordWrap(True)
        options = QLabel("Lesson Task: " + str(options_text), self)
        self.user_input = QPlainTextEdit(self)
        self.submit = QPushButton("Submit", self)
        go_back = QPushButton("Go Back", self)

        layout = QVBoxLayout()
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(desc, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch(1)
        layout.addWidget(content)
        layout.addStretch(1)
        layout.addWidget(options, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.user_input)
        layout.addStretch(1)
        layout.addWidget(self.submit)
        layout.addWidget(go_back)

        central.setObjectName("central_widget")
        title.setObjectName("title")
        desc.setObjectName("desc")
        content.setObjectName("content")

        self.setStyleSheet(
            """
            QMainWindow{
                background-color: white;
            }
            QWidget#central_widget{
                border: 2px solid;
                border-radius: 5px;
            }
            QLabel{
                color: black;
                font-weight: bold;
                font-size: 20px;
            }
            QLabel#title{
                font-size: 45px;
                text-decoration: underline;
            }
            QPlainTextEdit{
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

        self.submit.clicked.connect(_submit_lesson)
        go_back.clicked.connect(self.search)

    def init_settings(self):

        def set_connect_data():
            file_path = join(get_appdata_path(), "connect-data.txt")
            required_texts = (
                self.server_ip_text,
                self.server_port_text,
                self.server_type_text,
            )
            for text in required_texts:
                if text.text() == "":
                    self.show_message_box(
                        "error",
                        "Error saving connection data",
                        "Unable to connect data as not all parts are filled out.",
                    )
                    return

            with open(file_path, "wb") as file:
                data = f"{required_texts[0].text().strip()} {required_texts[1].text().strip()} {required_texts[2].text().strip()}"
                file.write(encrypt_file(data))

            self.show_message_box(
                "info",
                "Connection data",
                "Successfully saved connection data.\n"
                "Please restart the app for these changes to take effect.",
            )

        def clear_log():
            file_path = join(get_appdata_path(), "client.log")
            file_path_2 = join(get_appdata_path(), "client-module.log")

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("")

            except (FileNotFoundError, PermissionError) as e:
                print(e)

            try:
                with open(file_path_2, "w", encoding="utf-8") as f:
                    f.write("")

            except (FileNotFoundError, PermissionError) as e:
                print(e)

            print("Cleared log")
            self.show_message_box(
                "info", "Cleared log", "Log was successfully cleared."
            )

        def delete_lessons():
            file_path = join(get_appdata_path(), "lessons.json")

            try:
                with open(file_path, "wb") as f:
                    f.write(encrypt_file(""))

                self.show_message_box(
                    "info", "Lesson deletion", "All lessons were successfully deleted."
                )
                log_error("All lessons were successfully deleted.")

            except (FileNotFoundError, PermissionError) as e:
                log_error(e)
                print(e)

        def reset_leaderboard():
            file_path = join(get_appdata_path(), "leaderboards.json")

            try:
                with open(file_path, "wb") as f:
                    f.write(encrypt_file(""))

                self.show_message_box(
                    "info",
                    "Leaderboard deletion",
                    "All leaderboard data has successfully been deleted.",
                )
                log_error("All leaderboard data was successfully deleted.")

            except (FileNotFoundError, PermissionError) as e:
                log_error(e)
                print(e)

        def delete_all_data():
            delete_lessons()
            reset_leaderboard()
            clear_log()
            self.lessons_completed = 0
            self.points = 0.0

            file_path = join(get_appdata_path(), "connect-data.txt")
            file_path_2 = join(get_appdata_path(), "SAVE_DATA.dat")

            try:
                with open(file_path, "wb") as f:
                    f.write(encrypt_file(""))

            except (FileNotFoundError, PermissionError) as e:
                log_error(e)
                print(e)

            try:
                with open(file_path_2, "wb") as f:
                    f.write(encrypt_file(""))

            except (FileNotFoundError, PermissionError) as e:
                log_error(e)
                print(e)

            self.init_settings()
            self.show_message_box(
                "warning",
                "Data deletion",
                "All data was successfully reset.\n"
                "Please restart the app for these changes to take effect.",
            )

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        file_path = join(get_appdata_path(), "connect-data.txt")

        title = QLabel("Settings", self)
        title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        clear_log_button = QPushButton("Clear Logs ⚠️", self)
        clear_lessons_button = QPushButton("Delete ALL Lessons 🗑️", self)
        reset_leaderboard_button = QPushButton("Reset Leaderboard 🔄️🏆", self)
        clear_all_data = QPushButton("Reset ALL data 🚫", self)

        points_earned = QLabel(f"Points: {self.points:,.2f}", self)
        lessons_completed = QLabel(
            f"Lessons completed: {self.lessons_completed:,}", self
        )
        connection_status = QLabel(
            f"Connection Status: "
            f"{'Connected 🛜' if connectmod.is_connected() else 'Disconnected ❌'}"
        )

        points_earned.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        lessons_completed.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        connection_status.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.server_ip_text = QLineEdit(self)
        self.server_ip_text.setPlaceholderText("Enter SERVER IP")

        self.server_port_text = QLineEdit(self)
        self.server_port_text.setPlaceholderText("Enter SERVER PORT")

        self.server_type_text = QLineEdit(self)
        self.server_type_text.setPlaceholderText("Enter IP TYPE (IPv4/IPv6)")

        submit = QPushButton("Submit Data 💾", self)
        go_back = QPushButton("Go Back ↩️", self)

        try:
            with open(file_path, "rb") as file:
                file_data = file.read()
                if file_data:
                    file_data = decrypt_file(file_data).split()
                    self.server_ip_text.setText(str(file_data[0]))
                    self.server_port_text.setText(str(file_data[1]))
                    self.server_type_text.setText(str(file_data[2]))

        except (FileNotFoundError, PermissionError, IndexError) as e:
            log_error(e)

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(1)
        layout.addWidget(points_earned, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(lessons_completed, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(connection_status, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(clear_log_button)
        layout.addWidget(clear_lessons_button)
        layout.addWidget(reset_leaderboard_button)
        layout.addWidget(clear_all_data)
        layout.addSpacing(2)
        layout.addWidget(self.server_ip_text)
        layout.addWidget(self.server_port_text)
        layout.addWidget(self.server_type_text)
        layout.addWidget(submit)
        layout.addWidget(go_back)

        title.setObjectName("title")
        clear_log_button.setObjectName("clear_log")
        points_earned.setObjectName("points_earned")
        lessons_completed.setObjectName("lessons_completed")
        connection_status.setObjectName("connection_status")

        self.setStyleSheet(
            """
                            QMainWindow{
                                background-color: white;
                            }
                            QLabel{
                                color: black;
                                font-weight: bold;
                            }
                            QLabel#title{
                                font-size: 50px;
                                text-decoration: underline;
                            }
                            QLabel#points_earned{
                                font-size: 35px;
                            }
                            QLabel#lessons_completed{
                                font-size: 35px;
                            }
                            QLabel#connection_status{
                                font-size: 35px;
                            }
                            QPushButton{
                                background-color: hsl(0, 1%, 27%);
                                color: white;
                                border: 2px solid;
                                border-radius: 5px;
                                font-weight: bold;
                                font-size: 25px;
                            }
                            QPushButton#clear_log{
                                background-color: hsl(0, 92%, 53%);
                                color: white;
                                border: 2px solid;
                                border-radius: 5px;
                                font-weight: bold;
                                font-size: 25px;
                            }
                            QPushButton#clear_log:hover{
                                background-color: hsl(0, 92%, 73%);
                                color: white;
                                border: 2px solid;
                                border-radius: 5px;
                                font-weight: bold;
                                font-size: 25px;
                            }
                            QPushButton:hover{
                                background-color: hsl(0, 1%, 47%);
                                color: white;
                                border: 2px solid;
                                border-radius: 5px;
                            }
                            QLineEdit{
                                background-color: white;
                                color: black;
                                border: 2px solid;
                                border-radius: 5px;
                                font-size: 25px;
                            }
                        """
        )

        central.setLayout(layout)
        submit.clicked.connect(set_connect_data)
        go_back.clicked.connect(self.search)
        clear_log_button.clicked.connect(clear_log)
        clear_lessons_button.clicked.connect(delete_lessons)
        clear_all_data.clicked.connect(delete_all_data)
        reset_leaderboard_button.clicked.connect(reset_leaderboard)

    def press_button(self, id_l, max_points=0.0):
        if (
            str(self.user_input.toPlainText()).replace('"', "'").rstrip()
            == self.answer.rstrip()
        ):
            self.submit.setStyleSheet(
                "background-color: hsl(115, 100%, 70%)"
            )  # light green
            self.lessons_completed += 1
            self.points += round((float(max_points) / int(self.lesson_attempt)), 2)
            self.lesson_attempt = 1
            lesson = mark_lesson_finish(id_l)
            lesson["completed"] = "True"

            file_path = join(get_appdata_path(), "lessons.json")

            data = load_json(file_path)

            for idx, lsn in enumerate(data["lessons"]):
                if int(lsn["id"]) == id_l:
                    data["lessons"][idx] = lesson
                    break

            with open(file_path, "wb") as f:
                data = dumps(data)
                f.write(encrypt_file(data))

            self.save_data()
            self.reload_json()
            self.search()

        else:
            self.submit.setStyleSheet("background-color: hsl(0, 97%, 62%)")
            self.lesson_attempt += 1


if __name__ == "__main__":
    app = QApplication(sys_argv)
    window = MainWindow()
    window.show()
    sys_exit(app.exec())
