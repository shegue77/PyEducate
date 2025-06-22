from PySide6.QtWidgets import QMainWindow, QWidget, QLineEdit, QLabel, QPushButton, QApplication, QVBoxLayout, QPlainTextEdit
from PySide6.QtGui import Qt
from sys import argv as sys_argv, exit as sys_exit
from json import load, loads, dump, dumps, JSONDecodeError

class Editor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyEducate: Lesson Editor')
        self.id_input = 1
        self.edit_json_file = False
        self._initui()

    def list_lessons(self):
        pass

    def create_json(self):
        if not self.edit_json_file:
            title = str(self.title_name.text())
            mild_desc = str(self.description_text.text())
            content = str(self.content_text.toPlainText().replace('\n', '\\n'))
            question = '"' + str(self.quiz_question_text.text()) + '"'
            answer = '"' + str(self.quiz_answer_text.toPlainText().replace('\n', '\\n')) + '"'
        else:
            pass

        quiz = '[{"question": ' + question + ', "answer": ' + answer + '}]'

        def read_json():

            with open('lessons.json', 'r') as f:
                data = load(f)

            for lesson in data["lessons"]:
                for id_num in str(lesson["id"]):
                    if id_num == str(self.id_input):
                        self.id_input += 1
                        read_json()
                        return

        read_json()

        new_lesson = '{"id": ' + str(self.id_input) + ', "title": "' + title + '", "description": "' + mild_desc + '", "content": "' + content + '", "quiz": ' + quiz + '}'

        if type(new_lesson) is dict:
            try:
                dumps(new_lesson)
                print("✅ Dictionary is JSON serializable")
            except (TypeError, OverflowError) as e:
                print("❌ Not JSON serializable:", e)
                exit()

        else:
            try:
                new_lesson = loads(new_lesson)
                print("✅ JSON is valid")
            except JSONDecodeError as e:
                print("❌ Invalid JSON:", e)
                exit()

        # Load from file
        with open('lessons.json', 'r') as f:
            data = load(f)

        # Modify (e.g., add a lesson)
        data["lessons"].append(new_lesson)

        # Save back to file
        with open('lessons.json', 'w') as f:
            dump(data, f, indent=2)
            print('data written')

    def edit_json(self, id_n):
        with open('lessons.json', 'r') as file:
            data = load(file)

        for lesson in data['lessons']:
            if int(lesson['id']) == int(id_n):
                correct_lesson = lesson
                break

        title = correct_lesson['title']
        image_path = correct_lesson['image']
        description = correct_lesson['description']
        content = correct_lesson['content']

        try:
            for quiz in correct_lesson['quiz']:  # Loop over the quiz list
                print(quiz['question'])
                options_text = str(quiz['question'])
                answer = str(quiz['answer'])

        except Exception:
            pass

        return title, image_path, description, content, options_text, answer


    def del_json(self):
        id_input = self.id_input

        file_path = 'lessons.json'

        with open(file_path, 'r') as f:
            data = load(f)

        for lesson in data["lessons"]:
            for id_num in str(lesson["id"]):
                if id_num == str(id_input):
                    data["lessons"].remove(lesson)
                    with open(file_path, 'w') as f:
                        dump(data, f, indent=2)
                        print(f"Lesson with ID {id_num} is being deleted...")

        existing_ids = []

        for lesson in data["lessons"]:
            for id_num in str(lesson["id"]):
                existing_ids.append(id_num)

        try:
            if int(id_input) not in existing_ids:
                self.status.setText(f"✅ Lesson with ID {id_input} has been successfully deleted!")
            else:
                self.status.setText(f"❌ Lesson with ID {id_input} is unable to be removed!")

        except Exception:
            pass

    def _initui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title = QLabel('PyEducate: Lesson Maker/Editor', self)
        create = QPushButton('Create Lesson', self)
        edit = QPushButton('Edit Lesson', self)
        delete = QPushButton('Delete Lesson', self)
        list_l = QPushButton('List Lessons', self)
        settings = QPushButton('Settings', self)

        title.setObjectName('title')
        create.setObjectName('create')
        edit.setObjectName('edit')
        delete.setObjectName('delete')
        settings.setObjectName('settings')
        list_l.setObjectName('list_l')

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(create)
        layout.addWidget(edit)
        layout.addWidget(delete)
        layout.addWidget(list_l)
        layout.addWidget(settings)

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

        create.clicked.connect(self._initui_lesson)
        edit.clicked.connect(self._init_edit_prompt)
        delete.clicked.connect(self._init_del_menu)
        settings.clicked.connect(self._init_settings)

        central.setLayout(layout)

    def _list_lessons_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title_title = QLabel('PyEducate: Lesson List', self)

    def _initui_lesson(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title_title = QLabel('PyEducate: Lesson Maker', self)

        self.title_name = QLineEdit(self)
        self.title_name.setPlaceholderText('Enter Title (Required)')

        self.image_path = QLineEdit(self)
        self.image_path.setPlaceholderText('Enter Image Path (Optional)')

        self.description_text = QLineEdit(self)
        self.description_text.setPlaceholderText('Quick Description (Required)')

        self.content_text = QPlainTextEdit(self)
        self.content_text.setPlaceholderText('Full description and answers (Required, Can be Multi-line)')

        self.quiz_question_text = QLineEdit(self)
        self.quiz_question_text.setPlaceholderText('Quiz Question (Required, one question only)')

        self.quiz_answer_text = QPlainTextEdit(self)
        self.quiz_answer_text.setPlaceholderText('Quiz Answer (Required)')

        submit_data = QPushButton('Submit', self)
        go_back_del = QPushButton('Main Menu')

        layout.addWidget(title_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.title_name)
        layout.addWidget(self.image_path)
        layout.addWidget(self.description_text)
        layout.addWidget(self.content_text)
        layout.addWidget(self.quiz_question_text)
        layout.addWidget(self.quiz_answer_text)
        layout.addWidget(submit_data)
        layout.addWidget(go_back_del)

        title_title.setObjectName('title_title')

        self.setStyleSheet("""
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
                        """)

        go_back_del.clicked.connect(self._initui)
        submit_data.clicked.connect(self.create_json)

        central.setLayout(layout)

    def _init_edit_prompt(self):

        def _submit():
            self._init_edit_menu(self.id_name.text())

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title_title = QLabel('Enter Lesson ID', self)
        self.id_name = QLineEdit(self)
        self.id_name.setPlaceholderText('Enter ID')

        submit_data = QPushButton('Submit Data', self)
        go_back_edit = QPushButton('Main Menu', self)

        layout.addWidget(title_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.id_name)
        layout.addWidget(submit_data)
        layout.addWidget(go_back_edit)

        title_title.setObjectName('title')

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
                        """)

        submit_data.clicked.connect(_submit)
        go_back_edit.clicked.connect(self._initui)
        central.setLayout(layout)

    def _edit_file(self):
        self.del_json()
        self.create_json()

    def _init_edit_menu(self, id_n='0'):
        print(id_n)
        print(type(id_n))
        self.id_input = id_n

        text = self.edit_json(id_n)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title_title = QLabel('PyEducate: Lesson Editor', self)

        self.title_name = QLineEdit(self)
        self.title_name.setPlaceholderText('Edit Title')
        self.title_name.setText(str(text[0]))

        self.image_path = QLineEdit(self)
        self.image_path.setPlaceholderText('Edit Image Path')
        self.image_path.setText(str(text[1]))

        self.description_text = QLineEdit(self)
        self.description_text.setPlaceholderText('Edit Quick Description')
        self.description_text.setText(str(text[2]))

        self.content_text = QPlainTextEdit(self)
        self.content_text.setPlaceholderText('Edit full description and answers (Can be Multi-line)')
        self.content_text.setPlainText(str(text[3]))

        self.quiz_question_text = QLineEdit(self)
        self.quiz_question_text.setPlaceholderText('Edit Quiz Question (One question only)')
        self.quiz_question_text.setText(str(text[4]))

        self.quiz_answer_text = QPlainTextEdit(self)
        self.quiz_answer_text.setPlainText(str(text[5]))

        submit_data = QPushButton('Submit Data', self)
        go_back_edit = QPushButton('Main Menu', self)

        layout.addWidget(title_title)
        layout.addWidget(self.title_name)
        layout.addWidget(self.image_path)
        layout.addWidget(self.description_text)
        layout.addWidget(self.content_text)
        layout.addWidget(self.quiz_question_text)
        layout.addWidget(self.quiz_answer_text)
        layout.addWidget(submit_data)
        layout.addWidget(go_back_edit)

        title_title.setObjectName('title_title')

        self.setStyleSheet("""
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
                                """)

        go_back_edit.clicked.connect(self._initui)
        submit_data.clicked.connect(self._edit_file)

        central.setLayout(layout)

    def _init_del_menu(self):
        def _submit():
            self.id_input = self.id_input_data.text()
            self.del_json()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title = QLabel('PyEducate: Lesson Editor', self)
        self.id_input_data = QLineEdit(self)
        self.id_input_data.setPlaceholderText('Enter Lesson ID')
        delete_button = QPushButton('Delete Selected Lesson', self)
        self.status = QLabel('', self)
        go_back_del = QPushButton('Main Menu')

        delete_button.clicked.connect(_submit)
        go_back_del.clicked.connect(self._initui)

        title.setObjectName('title')

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.id_input_data)
        layout.addWidget(self.status)
        layout.addWidget(delete_button)
        layout.addWidget(go_back_del)

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
                        """)

        central.setLayout(layout)

    def _init_settings(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        title = QLabel('Settings', self)
        file_save = QLineEdit(self)
        file_save.setPlaceholderText('File Save Path')
        file_save.setText('%APPDATA%')
        file_save.setDisabled(True)
        go_back = QPushButton('Go Back', self)

        title.setObjectName('title')

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(file_save)
        layout.addWidget(go_back)
        go_back.clicked.connect(self._initui)

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
                        """)

        central.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys_argv)
    window = Editor()
    window.show()
    sys_exit(app.exec())