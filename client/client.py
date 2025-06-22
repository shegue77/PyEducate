from json import load as json_load
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPlainTextEdit, QVBoxLayout, QPushButton, QLineEdit
from PySide6.QtGui import Qt, QPixmap
import sys
from threading import Thread
import connectmod
from os import path as os_path
from PIL import Image
from time import sleep

with open('connect-data.txt', 'r') as f:
    SERVER_IP = str(f.readline().replace('\n', ''))
    SERVER_PORT = int(f.readline())
    IP_TYPE = str(f.readline())

def attempt_connect_loop(SERVER_IP, SERVER_PORT, IP_TYPE):
    while True:
        try:
            connectmod.start_client(SERVER_IP, SERVER_PORT, IP_TYPE)
            break
        except ConnectionError as e:
            print(f"{e} Retrying in 10 seconds...")
            sleep(10)

Thread(target=attempt_connect_loop, args=(SERVER_IP, SERVER_PORT, IP_TYPE), daemon=True).start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyEducate: School Edition')
        self.setContentsMargins(20, 20, 20, 20)
        self.data = None

        self.reload_json()
        self.enter_code()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os_path.abspath(".")
        return os_path.join(base_path, relative_path)

    def reload_json(self):
        with open('lessons.json', 'r') as file:
            self.data = json_load(file)
            print('reloaded')

    def submit_id_data(self):

        id_n = self.data_input.text()
        print(id_n)

        status = 'Fail'
        print(self.data['lessons'])
        for lesson in self.data['lessons']:
            try:
                if int(lesson['id']) == int(id_n):
                    correct_lesson = lesson
                    status = 'Success'
                    break
            except Exception as e:
                with open('lessons.json', 'r') as file:
                    self.data = json_load(file)
                    print('reloaded')
                print(e)
                break

        if status == 'Success':
            print('e')
            self._init_lesson(correct_lesson)
        else:
            with open('lessons.json', 'r') as file:
                self.data = json_load(file)
                print('reloaded')

    def enter_code(self):
        central = QWidget()
        self.setCentralWidget(central)

        text = QLabel('Access Lesson', self)
        self.data_input = QLineEdit(self)
        self.data_input.setPlaceholderText('Enter Lesson ID')
        submit_id = QPushButton('Submit Lesson ID', self)

        layout = QVBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self.data_input)
        layout.addWidget(submit_id)

        central.setLayout(layout)

        submit_id.clicked.connect(self.submit_id_data)

    def _init_lesson(self, lesson):

        options_text = ''
        for quiz in lesson['quiz']:  # Loop over the quiz list
            print(quiz['question'])
            options_text = quiz['question']
            self.answer = str(quiz['answer'])

        central = QWidget()
        self.setCentralWidget(central)

        title = QLabel(str(lesson['title']), self)
        desc = QLabel(str(lesson['description']), self)

        if str(lesson['image']) != 'False':
            try:
                image = QLabel()
                pixmap = QPixmap(self.resource_path(str(lesson['image'])))
                image_data = Image.open(str(lesson['image']))

                # Get the size of the image
                width, height = image_data.size
                image.setMaximumSize(width/2, height/2)
                image.setScaledContents(True)

                image.setPixmap(pixmap)
            except Exception:
                pass

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
        except:
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
        except:
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

    def press_button(self):
        if str(self.user_input.toPlainText()) == self.answer:
            self.submit.setStyleSheet('background-color: hsl(115, 100%, 70%)') # light green
        else:
            self.submit.setStyleSheet('background-color: hsl(0, 97%, 62%)')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())