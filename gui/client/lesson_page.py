from json import JSONDecodeError
from os.path import join, dirname, abspath
from os import makedirs

from PySide6.QtWidgets import QPushButton, QLabel, QTextEdit

from utils.crypto import encrypt_file, decrypt_file
from utils.client.storage import load_json, write_json, find_lesson, mark_lesson_finish
from utils.client.logger import log_error
from utils.client.paths import get_appdata_path


def get_points_data():
    save_data_path = join(get_appdata_path(), "SAVE_DATA.dat")
    try:
        with open(save_data_path, "rb") as f:
            save_data = decrypt_file(f.read()).strip().split()
            points = float(save_data[0])
            lessons_completed = int(save_data[1])

    except FileNotFoundError as fe:
        log_error(fe)
        with open(save_data_path, "wb") as f:
            f.write(encrypt_file("0 0"))
        points = 0.0
        lessons_completed = 0

    except (TypeError, IndexError) as ie:
        points = 0.0
        lessons_completed = 0
        log_error(ie)
    return points, lessons_completed


def resource_path(relative_path):
    # Get the directory of the current file (module)
    module_dir = dirname(abspath(__file__))

    return join(module_dir, relative_path)


def press_button(self, id_l, max_points=0.0):
    print("Lesson attempt: " + str(self.lesson_attempt))
    points, lessons_completed = get_points_data()
    submit_button = self.findChild(QPushButton, "ltl_submit")

    file_path = join(get_appdata_path(), "lessons.json")
    data = load_json(file_path)
    lesson = mark_lesson_finish(id_l)

    for idx, lsn in enumerate(data["lessons"]):
        if int(lsn["id"]) == id_l:
            data["lessons"][idx] = lesson
            break
    answer = ""
    for quiz in lesson["quiz"]:
        answer = quiz["answer"]

    user_input = self.findChild(QTextEdit, "ltl_answer")
    if (
        str(user_input.toPlainText()).replace('"', "'").rstrip()
        == answer.replace('"', "'").rstrip()
    ):
        lessons_completed += 1
        print(
            "Points: " + str(round((float(max_points) / int(self.lesson_attempt)), 2))
        )
        points += round((float(max_points) / int(self.lesson_attempt)), 2)
        self.lesson_attempt = 1
        lesson["completed"] = "True"

        write_json(file_path, data)

        file_path = str(join(get_appdata_path(), "SAVE_DATA.dat"))
        with open(file_path, "wb") as file:
            write_data = f"{str(points)} {str(lessons_completed)}"
            file.write(encrypt_file(write_data))
        print("Point data saved successfully")

        submit_button.setStyleSheet(
            "background-color: hsl(115, 100%, 70%)"
        )  # light green
        return True

    else:
        self.lesson_attempt += 1
        submit_button.setStyleSheet("background-color: hsl(0, 97%, 62%)")
        return False


def init_lesson(self, lesson, ui):

    def _submit_lesson():
        submit.setDisabled(True)
        try:
            is_correct = press_button(self, int(lesson["id"]), float(lesson["points"]))

        except Exception as e:
            log_error(e)
            is_correct = press_button(self, int(lesson["id"]))
        if is_correct:
            self.stacked_widget.setCurrentWidget(ui.lessons_page)
        submit.setDisabled(False)
        init_lesson_page(self, ui)

    options_text = ""
    for quiz in lesson["quiz"]:  # Loop over the quiz list
        options_text = quiz["question"]

    self.findChild(QLabel, "ltl_title").setText(str(lesson["title"]))
    self.findChild(QLabel, "ltl_subtitle").setText(str(lesson["description"]))

    self.findChild(QLabel, "ltl_desc").setText(
        str(lesson["content"].replace("\\n", "\n"))
    )
    self.findChild(QLabel, "ltl_l_task").setText("Lesson Task: " + str(options_text))
    submit = self.findChild(QPushButton, "ltl_submit")
    submit.setStyleSheet(
        "padding: 10px; background-color: #040f13; border-radius: 10px;"
    )

    self.stacked_widget.setCurrentWidget(ui.l_type_lesson)
    print("set lesson page")

    # Disconnect all slots from this button's clicked signal
    try:
        submit.clicked.disconnect()
    except Exception:
        pass  # No connections yet
    submit.clicked.connect(_submit_lesson)


def _get_lessons_for_page(page_number):
    file_path = join(get_appdata_path(), "lessons.json")
    try:
        data = load_json(file_path)

    except (FileNotFoundError, JSONDecodeError) as fe:
        log_error(fe)
        print(fe)
        print()
        makedirs(join(get_appdata_path(), "images"), exist_ok=True)
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


# Lesson page setup functions
def _list_lesson_ids():
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


def _get_widgets(self):
    button_1: QPushButton = self.findChild(QPushButton, "button_1")
    button_2: QPushButton = self.findChild(QPushButton, "button_2")
    button_3: QPushButton = self.findChild(QPushButton, "button_3")
    button_4: QPushButton = self.findChild(QPushButton, "button_4")
    button_5: QPushButton = self.findChild(QPushButton, "button_5")
    button_6: QPushButton = self.findChild(QPushButton, "button_6")
    button_7: QPushButton = self.findChild(QPushButton, "button_7")
    button_8: QPushButton = self.findChild(QPushButton, "button_8")
    previous_page: QPushButton = self.findChild(QPushButton, "previous_page")
    next_page: QPushButton = self.findChild(QPushButton, "next_page")

    label_1: QLabel = self.findChild(QLabel, "label_1")
    label_2: QLabel = self.findChild(QLabel, "label_2")
    label_3: QLabel = self.findChild(QLabel, "label_3")
    label_4: QLabel = self.findChild(QLabel, "label_4")
    label_5: QLabel = self.findChild(QLabel, "label_5")
    label_6: QLabel = self.findChild(QLabel, "label_6")
    label_7: QLabel = self.findChild(QLabel, "label_7")
    label_8: QLabel = self.findChild(QLabel, "label_8")
    total_l_pages: QLabel = self.findChild(QLabel, "total_l_pages")

    buttons = (
        button_1,
        button_2,
        button_3,
        button_4,
        button_5,
        button_6,
        button_7,
        button_8,
        previous_page,
        next_page,
    )
    labels = (
        label_1,
        label_2,
        label_3,
        label_4,
        label_5,
        label_6,
        label_7,
        label_8,
        total_l_pages,
    )

    return buttons, labels


def submit_id_data(self, id_n, ui):
    print("submit_id_data called id_n with:", repr(id_n), type(id_n))
    try:
        id_n = int(id_n)
    except Exception as e:
        print("Bad id_n; expected int/str:", e)
        return

    print("a")
    status = "Fail"
    file_path = join(get_appdata_path(), "lessons.json")

    try:
        data = load_json(file_path)

    except (FileNotFoundError, JSONDecodeError) as fe:
        log_error(fe)
        makedirs(join(get_appdata_path(), "images"), exist_ok=True)
        data = {"lessons": []}
        write_json(file_path, data)

    correct_lesson = ""
    for lesson in data["lessons"]:
        if int(lesson["id"]) == int(id_n):
            correct_lesson = lesson
            status = "Success"
            break

    if status == "Success":
        print("success")
        init_lesson(self, correct_lesson, ui)
    else:
        print("failure")


def init_lesson_page(self, ui):
    total_pages = _list_lesson_ids()

    def setup_page():
        pages_lessons = _get_lessons_for_page(self.page)

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

    while True:
        if len(passed_lessons) < 8:
            passed_lessons.append(None)
        else:
            break

    buttons, labels = _get_widgets(self)

    for idx, lesson in enumerate(passed_lessons, start=0):
        if lesson is not None:
            lesson_data = find_lesson(lesson)
            try:
                labels[idx].setText(
                    f"{lesson_data[1]}\n{lesson_data[3]}\nID: {lesson_data[0]}\nCompleted: {lesson_data[7]}"
                )
            except IndexError as ie:
                log_error(ie)
                labels[idx].setText("Error loading lesson!")
                return None

            buttons[idx].setText("Start lesson")
            buttons[idx].setDisabled(False)
        else:
            labels[idx].setText("Placeholder")
            buttons[idx].setText("Placeholder")
            buttons[idx].setDisabled(True)

        if lesson is not None:
            lesson_data = find_lesson(lesson)
            if str(lesson_data[7]) == "True":
                buttons[idx].setDisabled(True)
                buttons[idx].setText("Lesson complete")

    if total_pages is None:
        total_pages = 1

    labels[-1].setText(f"Page: {self.page}/{total_pages}")

    if self.page >= total_pages:
        buttons[-1].setDisabled(True)
    else:
        buttons[-1].setDisabled(False)

    if self.page <= 1:
        buttons[-2].setDisabled(True)
    else:
        buttons[-2].setDisabled(False)

    for btn, lesson_id in zip(buttons, passed_lessons):
        # Disconnect all slots from this button's clicked signal
        try:
            btn.clicked.disconnect()
        except Exception:
            pass  # No connections yet

        if lesson_id is not None:
            # Connect new lambda capturing the current lesson_id
            btn.clicked.connect(
                lambda _, lesson_i=lesson_id: submit_id_data(self, lesson_i, ui)
            )

    return buttons[-2], buttons[-1], total_pages
