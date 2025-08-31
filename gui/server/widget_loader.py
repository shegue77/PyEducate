from os.path import join

from PySide6.QtWidgets import (
    QStackedWidget,
    QFrame,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QLabel,
)

from network.server.network import get_local_ip_address
from utils.crypto import decrypt_file
from utils.server.paths import get_appdata_path
from utils.server.logger import log_error
from utils.server.storage import (
    del_lesson,
    create_json,
    lesson_req_checks,
    get_username,
)
from utils.server.admin import list_banned, ban_user, unban_user


def init_lesson(self, all_texts):
    title: QLabel = self.findChild(QLabel, "title_p")
    subtitle: QLabel = self.findChild(QLabel, "subtitle_p")
    desc: QLabel = self.findChild(QLabel, "desc_p")
    task: QLabel = self.findChild(QLabel, "lesson_q_p")
    answer: QTextEdit = self.findChild(QTextEdit, "lesson_a_p")

    title.setText(all_texts[1])
    subtitle.setText(all_texts[3])
    desc.setText(all_texts[4].replace("\\n", "\n"))
    task.setText(all_texts[5])
    answer.setText(
        f"Lesson answer here (case and space sensitive)\nAnswer (not shown to students):\n{all_texts[6]}"
    )


def _load_edit_page(self):
    title_text: QLineEdit = self.findChild(QLineEdit, "title_text_2")
    points_text: QLineEdit = self.findChild(QLineEdit, "points_text_2")
    subtitle_text: QLineEdit = self.findChild(QLineEdit, "subtitle_text_2")
    quiz_q_text: QLineEdit = self.findChild(QLineEdit, "quiz_q_text_2")
    desc_text: QTextEdit = self.findChild(QTextEdit, "desc_text_2")
    quiz_a_text: QTextEdit = self.findChild(QTextEdit, "quiz_a_text_2")

    return title_text, subtitle_text, points_text, desc_text, quiz_q_text, quiz_a_text


def load_lesson_page(self, all_texts):
    title_text, subtitle_text, points_text, desc_text, quiz_q_text, quiz_a_text = (
        _load_edit_page(self)
    )

    title_text.setText(all_texts[1])
    subtitle_text.setText(all_texts[3])
    desc_text.setText(all_texts[4])
    quiz_q_text.setText(all_texts[5])
    quiz_a_text.setText(all_texts[6])
    points_text.setText(all_texts[7])


def edit_lesson(self, ui):
    all_texts = _load_edit_page(self)
    did_pass = lesson_req_checks(all_texts)

    edit_id_text: QLineEdit = self.findChild(QLineEdit, "edit_id_text")

    if not did_pass:
        print("Not all required fields have been filled out!")
        edit_id_text.setText(f"Successfully edited lesson ID {edit_id_text.text()}")
        return

    del_lesson(edit_id_text.text())

    create_json(edit_id_text.text(), all_texts)
    edit_id_text.setText(f"Successfully edited lesson ID {edit_id_text.text()}")

    change_page(self, ui.lesson_editor, False)


def load_admin_page(self):
    self.findChild(QTextEdit, "ip_blacklist_text").setText(str(list_banned()))


def ban_ip_addr(self):
    ip_addr_text: QLineEdit = self.findChild(QLineEdit, "ip_addr_text")
    ban_reason_text: QLineEdit = self.findChild(QLineEdit, "ban_reason_text")
    ban_severity_text: QLineEdit = self.findChild(QLineEdit, "ban_severity_text")

    texts: list = [
        ip_addr_text.text(),
        ban_reason_text.text(),
        ban_severity_text.text(),
    ]
    ban_user(texts, is_gui=True)

    ip_addr_text.setText("")
    ban_reason_text.setText("")
    ban_severity_text.setText("")

    load_admin_page(self)


def unban_ip_addr(self):
    ip_addr_text: QLineEdit = self.findChild(QLineEdit, "ip_addr_text")
    print(unban_user(ip_addr_text.text()))

    ip_addr_text.setText("")

    load_admin_page(self)


def _load_settings_page(self):
    full_path = get_appdata_path()
    try:
        with open(join(full_path, "connect-data.txt"), "rb") as f:
            data = decrypt_file(f.read()).strip().splitlines()
            server_port = data[0]
            ip_type = data[1]
            try:
                server_ip = data[2]
            except IndexError as ie:
                log_error(ie)
                server_ip = get_local_ip_address(ip_type)
    except FileNotFoundError as fe:
        log_error(fe)
        server_port = ""
        ip_type = ""
        server_ip = ""

    try:
        username = get_username()
    except FileNotFoundError as fe:
        log_error(fe)
        username = ""

    self.findChild(QLineEdit, "ip_setting").setText(str(server_ip))
    self.findChild(QLineEdit, "port_setting").setText(str(server_port))
    self.findChild(QLineEdit, "ip_type_setting").setText(str(ip_type))
    self.findChild(QLineEdit, "user_setting").setText(username)


def change_page(self, page, change_menu: bool = True, ui_name=None):
    self.stacked_widget.setCurrentWidget(page)
    if change_menu:
        self.toggle_menu()

    if ui_name is not None:
        if ui_name == "settings_page":
            _load_settings_page(self)
        elif ui_name == "home_page":
            home_text: QLabel = self.findChild(QLabel, "home_text")
            try:
                username = get_username()
                if username.strip() != "":
                    home_text.setText(
                        f"Welcome back to PyEducate, {username}! We're excited to have you!"
                    )
                else:
                    home_text.setText(
                        "Welcome to PyEducate! We're excited to have you! Let's get started!\n\nTo get started, navigate to Menu -> Lesson Editor"
                    )

            except FileNotFoundError:
                home_text.setText(
                    "Welcome to PyEducate! We're excited to have you! Let's get started!\n\nTo get started, navigate to Menu -> Lesson Editor"
                )
        elif ui_name == "admin_page":
            load_admin_page(self)


def get_widgets(self, ui):
    stacked_widget: QStackedWidget = self.findChild(QStackedWidget, "stackedWidget")
    side_menu: QFrame = self.findChild(QFrame, "side_menu")
    menu_btn: QPushButton = self.findChild(QPushButton, "pushButton")

    about_button: QPushButton = self.findChild(QPushButton, "about_button")
    server_panel: QPushButton = self.findChild(QPushButton, "server_panel_button")
    settings_button: QPushButton = self.findChild(QPushButton, "settings_button")
    lesson_editor: QPushButton = self.findChild(QPushButton, "lesson_editor_button")
    admin_panel: QPushButton = self.findChild(QPushButton, "admin_panel_button")
    home_button: QPushButton = self.findChild(QPushButton, "home_button")
    create_lesson_page: QPushButton = self.findChild(
        QPushButton, "create_lesson_page_b"
    )
    list_l_button: QPushButton = self.findChild(QPushButton, "list_l_button")
    del_l_button: QPushButton = self.findChild(QPushButton, "del_l_button")

    start_server_b: QPushButton = self.findChild(QPushButton, "start_server_b")
    stop_server_b: QPushButton = self.findChild(QPushButton, "stop_server_b")
    get_lesson_info: QPushButton = self.findChild(QPushButton, "get_lesson_info_b")
    edit_l_button: QPushButton = self.findChild(QPushButton, "edit_l_button")
    create_lesson_b_2: QPushButton = self.findChild(QPushButton, "create_lesson_b_2")
    refresh_client_list: QPushButton = self.findChild(
        QPushButton, "refresh_client_list"
    )
    run_cmd: QPushButton = self.findChild(QPushButton, "run_cmd")

    import_lessons_b: QPushButton = self.findChild(QPushButton, "import_lessons_b")
    export_lessons_b: QPushButton = self.findChild(QPushButton, "export_lessons_b")

    create_lesson: QPushButton = self.findChild(QPushButton, "create_lesson_b")
    title_text: QLineEdit = self.findChild(QLineEdit, "title_text")
    points_text: QLineEdit = self.findChild(QLineEdit, "points_text")
    subtitle_text: QLineEdit = self.findChild(QLineEdit, "subtitle_text")
    quiz_q_text: QLineEdit = self.findChild(QLineEdit, "quiz_q_text")
    desc_text: QTextEdit = self.findChild(QTextEdit, "desc_text")
    quiz_a_text: QTextEdit = self.findChild(QTextEdit, "quiz_a_text")

    ban_ip_b: QPushButton = self.findChild(QPushButton, "ban_ip_b")
    unban_ip_b: QPushButton = self.findChild(QPushButton, "unban_ip_b")

    # Connect buttons
    server_panel.clicked.connect(lambda: change_page(self, ui.server_panel))
    admin_panel.clicked.connect(
        lambda: change_page(self, ui.admin_page, ui_name="admin_page")
    )
    lesson_editor.clicked.connect(lambda: change_page(self, ui.lesson_editor))
    settings_button.clicked.connect(
        lambda: change_page(self, ui.settings_page, ui_name="settings_page")
    )
    about_button.clicked.connect(lambda: change_page(self, ui.about_page))
    home_button.clicked.connect(
        lambda: change_page(self, ui.home_page, ui_name="home_page")
    )
    create_lesson_page.clicked.connect(
        lambda: change_page(self, ui.create_lesson_page, False)
    )
    ban_ip_b.clicked.connect(lambda: ban_ip_addr(self))
    unban_ip_b.clicked.connect(lambda: unban_ip_addr(self))

    return (
        stacked_widget,
        side_menu,
        menu_btn,
        server_panel,
        create_lesson_page,
        title_text,
        points_text,
        subtitle_text,
        desc_text,
        quiz_a_text,
        quiz_q_text,
        create_lesson,
        list_l_button,
        del_l_button,
        get_lesson_info,
        edit_l_button,
        create_lesson_b_2,
        start_server_b,
        stop_server_b,
        run_cmd,
        refresh_client_list,
        import_lessons_b,
        export_lessons_b
    )
