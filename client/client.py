import sys
from json import load as json_load, dump
from threading import Thread
from time import sleep
from os import getenv, makedirs
from os.path import exists as os_path_exists

import connectmod
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPlainTextEdit, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout
from PySide6.QtGui import Qt, QPixmap, QColor

def get_appdata_path():
    path_to_appdata = getenv('APPDATA')
    if os_path_exists(path_to_appdata + "\\PyEducate"):
        if os_path_exists(path_to_appdata + "\\PyEducate\\client"):
            full_path_data = path_to_appdata + "\\PyEducate\\client"
        else:
            makedirs(path_to_appdata + "\\PyEducate\\client")
            full_path_data = path_to_appdata + "\\PyEducate\\client"
    else:
        makedirs(path_to_appdata + "\\PyEducate")
        makedirs(path_to_appdata + "\\PyEducate\\client")
        full_path_data = path_to_appdata + "\\PyEducate\\client"

    return full_path_data

def disconnect():
    connectmod.close_client()

def attempt_connect_loop(SERVER_IP, SERVER_PORT, IP_TYPE):
    while True:
        try:
            connectmod.start_client(SERVER_IP, SERVER_PORT, IP_TYPE)
            break
        except (ConnectionError, ConnectionRefusedError, ConnectionResetError) as e:
            try:
                connectmod.close_client()
            except Exception:
                pass
            print(f"{e} Retrying in 10 seconds...")
            sleep(10)


try:
    with open(f'{get_appdata_path()}\\connect-data.txt', 'r', encoding='utf-8') as f:
        SERVER_IP = str(f.readline().replace('\n', ''))
        SERVER_PORT = int(f.readline().replace('\n', ''))
        IP_TYPE = str(f.readline().replace('\n', ''))

    thread = Thread(target=attempt_connect_loop, args=(SERVER_IP, SERVER_PORT, IP_TYPE), daemon=True).start()

except FileNotFoundError as fe:
    print(f'[!!] Connect data not found!\n{fe}')

except ValueError as ve:
    print(f'[!!] Corrupted data!\n{ve}')
    with open(f'{get_appdata_path()}\\connect-data.txt', 'w', encoding='utf-8') as f:
        f.write('')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyEducate: School Edition')
        self.setContentsMargins(20, 20, 20, 20)
        self.data = None
        self.page = 1
        self.points = 0

        self.reload_json()
        self.search()

    def closeEvent(self, event):
        try:
            connectmod.close_client()
        except Exception:
            pass
        event.accept()

    @staticmethod
    def get_appdata_path():
        path_to_appdata = getenv('APPDATA')
        if os_path_exists(path_to_appdata + "\\PyEducate"):
            if os_path_exists(path_to_appdata + "\\PyEducate\\client"):
                full_path_data = path_to_appdata + "\\PyEducate\\client"
            else:
                makedirs(path_to_appdata + "\\PyEducate\\client")
                full_path_data = path_to_appdata + "\\PyEducate\\client"
        else:
            makedirs(path_to_appdata + "\\PyEducate")
            makedirs(path_to_appdata + "\\PyEducate\\client")
            full_path_data = path_to_appdata + "\\PyEducate\\client"

        return full_path_data

    def reload_json(self):
        file_path = f'{get_appdata_path()}\\lessons.json'
        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                self.data = json_load(file)
                print('reloaded')
        except FileNotFoundError as fe:
            print(fe)
            print()
            makedirs(str(get_appdata_path() + '\\images'), exist_ok=True)
            if not os_path_exists(file_path):
                with open(file_path, 'w', encoding="utf-8") as file:
                    data = {"lessons":[]}
                    dump(data, file)
                    print('reloaded')

    def submit_id_data(self, id_n):

        status = 'Fail'
        file_path = f'{get_appdata_path()}\\lessons.json'
        for lesson in self.data['lessons']:
            if int(lesson['id']) == int(id_n):
                correct_lesson = lesson
                status = 'Success'
                break

            try:
                with open(file_path, 'r', encoding="utf-8") as file:
                    self.data = json_load(file)
                    print('reloaded')

            except FileNotFoundError as fe:
                print(fe)
                print()
                makedirs(str(get_appdata_path() + '\\images'), exist_ok=True)
                if not os_path_exists(file_path):
                    with open(file_path, 'w', encoding="utf-8") as file:
                        data = {"lessons":[]}
                        dump(data, file)

            except Exception as e:
                with open(file_path, 'r', encoding="utf-8") as file:
                    self.data = json_load(file)
                    print('reloaded')
                print(e)
                break

        if status == 'Success':
            self._init_lesson(correct_lesson)
        else:
            try:
                with open(file_path, 'r', encoding="utf-8") as file:
                    self.data = json_load(file)
                    print('reloaded')

            except FileNotFoundError as fe:
                print(fe)
                print()
                makedirs(str(get_appdata_path() + '\\images'), exist_ok=True)
                if not os_path_exists(file_path):
                    with open(file_path, 'w', encoding="utf-8") as file:
                        data = {"lessons":[]}
                        dump(data, file)

    @staticmethod
    def get_lessons_for_page(page_number):
        file_path = f'{get_appdata_path()}\\lessons.json'
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                data = json_load(f)

        except FileNotFoundError as fe:
            print(fe)
            print()
            makedirs(str(get_appdata_path() + '\\images'), exist_ok=True)
            if not os_path_exists(file_path):
                with open(file_path, 'w', encoding="utf-8") as file:
                    data = {"lessons":[]}
                    dump(data, file)
            return []

        items_per_page = 4
        start_index = (page_number - 1) * items_per_page
        end_index = start_index + items_per_page
        ids = []
        try:
            for lesson in data["lessons"][start_index:end_index]:
                ids.append(lesson["id"])
        except TypeError:
            return [None]
        return ids

    @staticmethod
    def list_lesson_ids():
        file_path = f'{get_appdata_path()}\\lessons.json'
        def create_json():
            with open(file_path, 'w', encoding="utf-8") as file:
                json_data = {"lessons":[]}
                dump(json_data, file, indent=4)

        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                data = json_load(f)

        except FileNotFoundError as fe:
            print(fe)
            print()
            #makedirs(str(get_appdata_path() + '\\images'), exist_ok=True)
            create_json()
            return 1

        whole_data = []
        try:
            print(data["lessons"])
        except TypeError:
            return None
        pages = (len(data["lessons"]) + 4 - 1) // 4
        for lesson in data["lessons"]:
            whole_data.append(int(lesson["id"]))

        return pages

    @staticmethod
    def find_lesson(lesson_id):
        file_path = f'{get_appdata_path()}\\lessons.json'
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                data = json_load(f)
        except FileNotFoundError as fe:
            print(fe)
            print()
            makedirs(str(get_appdata_path() + '\\images'), exist_ok=True)
            if not os_path_exists(file_path):
                with open(file_path, 'w', encoding="utf-8") as file:
                    data = {"lessons":[]}
                    dump(data, file)
                return None

        for lesson in data['lessons']:
            try:
                if int(lesson['id']) == int(lesson_id):
                    for quiz in lesson['quiz']:  # Loop over the quiz list
                        print(quiz['question'])

                        return str(lesson['id']), str(lesson['title']), str(lesson['image']), str(lesson['description']), str(lesson['content']), str(quiz['question']), str(quiz['answer'])
            except Exception as e:
                print(e)
                return None

    def search(self):
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

            return [None, None, None, None]

        while True:
            result = setup_page()
            if result is not None:
                passed_lessons = result
                break

        def next_page_set(total_page: int):
            print(total_page)
            print(self.page >= total_page)
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
        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout(self)
        right_layout = QVBoxLayout(self)
        bottom_layout = QVBoxLayout(self)

        search_bar = QLineEdit(self)
        search_bar.setPlaceholderText("Enter lesson title")
        search_bar.setDisabled(True)

        submit_search = QPushButton('Search', self)
        submit_search.setDisabled(True)

        reload_lessons = QPushButton('Reload lessons', self)

        top_layout.addWidget(search_bar)
        top_layout.addWidget(submit_search)
        top_layout.addWidget(reload_lessons)

        while True:
            if len(passed_lessons) < 4:
                passed_lessons.append(None)
            else:
                break

        for idx, lesson in enumerate(passed_lessons):
            image = QLabel()

            if lesson is not None:
                data = self.find_lesson(lesson)
                print(data[1])
                text = QLabel(f"{data[1]}\n{data[3]}\nID: {data[0]}")

                if data[2] != 'False':
                    try:
                        pixmap = QPixmap(f'{self.get_appdata_path()}\\images\\{str(data[2])}')
                        image.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                        image.setMaximumSize(120, 120)
                        image.setScaledContents(True)
                    except Exception as e:
                        print(e)
                        makedirs(str(get_appdata_path() + '\\images'), exist_ok=True)
                        pixmap = QPixmap(120, 120)
                        pixmap.fill(QColor("white"))
                    finally:
                        image.setPixmap(pixmap)

                else:
                    pass
            else:
                text = QLabel("Placeholder\n????????\nID: ??")

            if idx == 0 or idx == 1:
                left_layout.addWidget(image)
                left_layout.addWidget(text)
                if idx == 0:
                    button_1 = QPushButton('Start lesson', self)
                    left_layout.addWidget(button_1)

                    if passed_lessons[idx] is None:
                        button_1.setDisabled(True)
                    else:
                        button_1.setDisabled(False)
                else:
                    button_2 = QPushButton('Start lesson', self)
                    left_layout.addWidget(button_2)

                    if passed_lessons[idx] is None:
                        button_2.setDisabled(True)
                    else:
                        button_2.setDisabled(False)
            else:
                right_layout.addWidget(image)
                right_layout.addWidget(text)
                if idx == 2:
                    button_3 = QPushButton('Start lesson', self)
                    right_layout.addWidget(button_3)
                    if passed_lessons[idx] is None:
                        button_3.setDisabled(True)
                    else:
                        button_3.setDisabled(False)
                else:
                    button_4 = QPushButton('Start lesson', self)
                    right_layout.addWidget(button_4)
                    if passed_lessons[idx] is None:
                        button_4.setDisabled(True)
                    else:
                        button_4.setDisabled(False)

        if total_pages is None or total_pages == 0:
            total_pages = 1

        total_pages_text = QLabel(f"Page: {self.page}/{total_pages}", self)
        bottom_layout.addWidget(total_pages_text)

        previous_page = QPushButton('Previous Page', self)
        bottom_layout.addWidget(previous_page)

        next_page = QPushButton('Next Page', self)
        bottom_layout.addWidget(next_page)

        settings = QPushButton('Settings', self)
        bottom_layout.addWidget(settings)

        if self.page >= total_pages:
            next_page.setDisabled(True)
        else:
            next_page.setDisabled(False)

        if self.page <= 1:
            previous_page.setDisabled(True)
        else:
            previous_page.setDisabled(False)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        all_layouts.addLayout(top_layout)
        all_layouts.addLayout(main_layout)
        all_layouts.addLayout(bottom_layout)

        self.setStyleSheet("""
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
                    }
                    QLabel#title{
                        font-size: 45px;
                    }
                    QLabel#desc{
                        font-size: 20px;
                    }
                    QLineEdit{
                        background-color: white;
                        color: black;
                        border: 1px solid;
                        border-radius: 5px;
                        font-size: 10px;
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
                """)

        central.setLayout(all_layouts)

        if passed_lessons[0] is not None:
            button_1.clicked.connect(lambda: self.submit_id_data(passed_lessons[0]))
        if passed_lessons[1] is not None:
            button_2.clicked.connect(lambda: self.submit_id_data(passed_lessons[1]))
        if passed_lessons[2] is not None:
            button_3.clicked.connect(lambda: self.submit_id_data(passed_lessons[2]))
        if passed_lessons[3] is not None:
            button_4.clicked.connect(lambda: self.submit_id_data(passed_lessons[3]))

        previous_page.clicked.connect(previous_page_set)
        next_page.clicked.connect(lambda: next_page_set(total_pages))
        reload_lessons.clicked.connect(self.search)
        settings.clicked.connect(self._init_settings)

    def _init_lesson(self, lesson):

        options_text = ''
        for quiz in lesson['quiz']:  # Loop over the quiz list
            options_text = quiz['question']
            self.answer = str(quiz['answer'])

        central = QWidget()
        self.setCentralWidget(central)

        title = QLabel(str(lesson['title']), self)
        desc = QLabel(str(lesson['description']), self)

        if str(lesson['image']) != 'False':
            print('e_')
            try:
                image = QLabel()
                pixmap = QPixmap(f'{get_appdata_path()}\\images\\{str(lesson['image'])}')

                # Get the size of the image
                image.setMaximumSize(240, 240)
                image.setScaledContents(True)

                image.setPixmap(pixmap)

            except FileNotFoundError as fe:
                makedirs(str(get_appdata_path() + '\\images'), exist_ok=True)
                print(fe)

            except Exception as e:
                print(e)

        content = QLabel(str(lesson['content']).replace('\\n', '\n'), self)
        options = QLabel(str(options_text), self)
        self.user_input = QPlainTextEdit(self)
        self.submit = QPushButton('Submit', self)
        go_back = QPushButton('Go Back', self)

        layout = QVBoxLayout()
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(desc, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)
        try:
            layout.addWidget(image, alignment=Qt.AlignmentFlag.AlignHCenter)
        except Exception:
            pass

        layout.addStretch(1)
        layout.addWidget(content, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)
        layout.addWidget(options, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.user_input, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)
        layout.addWidget(self.submit)
        layout.addWidget(go_back)

        central.setObjectName('central_widget')
        title.setObjectName('title')
        desc.setObjectName('desc')
        content.setObjectName('content')
        try:
            image.setObjectName('image')
        except Exception:
            pass

        self.setStyleSheet("""
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
            }
            QLabel#title{
                font-size: 45px;
            }
            QLabel#desc{
                font-size: 20px;
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
        """)

        central.setLayout(layout)

        self.submit.clicked.connect(self.press_button)
        go_back.clicked.connect(self.search)

    def _init_settings(self):
        def set_connect_data():
            file_path = get_appdata_path() + '\\connect-data.txt'
            required_texts = (self.server_ip_text, self.server_port_text, self.server_type_text)
            for text in required_texts:
                if text.text() == '':
                    return

            with open(file_path, 'w') as file:
                data = f'{required_texts[0].text()}\n{required_texts[1].text()}\n{required_texts[2].text()}'
                file.write(data)


        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        file_path = get_appdata_path() + '\\connect-data.txt'

        title = QLabel('Settings', self)
        self.server_ip_text = QLineEdit(self)
        self.server_ip_text.setPlaceholderText('Enter SERVER IP')

        self.server_port_text = QLineEdit(self)
        self.server_port_text.setPlaceholderText('Enter SERVER PORT')

        self.server_type_text = QLineEdit(self)
        self.server_type_text.setPlaceholderText('Enter IP TYPE (IPv4/IPv6)')

        submit = QPushButton('Submit Data', self)
        go_back = QPushButton('Go Back', self)

        try:
            with open(file_path, 'r') as file:
                self.server_ip_text.setText(file.readline())
                self.server_port_text.setText(file.readline())
                self.server_type_text.setText(file.readline())

        except (FileNotFoundError, PermissionError):
            pass

        title.setObjectName('title')

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.server_ip_text)
        layout.addWidget(self.server_port_text)
        layout.addWidget(self.server_type_text)
        layout.addWidget(submit)
        layout.addWidget(go_back)

        self.setStyleSheet("""
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
                        """)

        central.setLayout(layout)
        submit.clicked.connect(set_connect_data)
        go_back.clicked.connect(self.search)

    def press_button(self):
        if str(self.user_input.toPlainText()).replace('"', "'") == self.answer:
            self.submit.setStyleSheet('background-color: hsl(115, 100%, 70%)') # light green
        else:
            self.submit.setStyleSheet('background-color: hsl(0, 97%, 62%)')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())