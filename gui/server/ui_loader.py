from os.path import abspath, join, dirname
from PySide6.QtWidgets import QMainWindow, QTextEdit, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import (
    QFile,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
)
from PySide6.QtUiTools import QUiLoader

from .widget_loader import (
    get_widgets,
    change_page,
    edit_lesson,
    init_lesson,
    load_lesson_page,
)
from utils.server.storage import (
    list_lessons,
    find_lesson,
    write_save_data,
    create_json,
    del_lesson,
)
from utils.server.logger import log_error
from network.server.network import get_server_data

from network.server.server import (
    start_server,
    process_command,
    disconnect,
    show_clients_list,
)

# Loads all icons
import gui.server.icons_loader

# ----- CONFIG -----
MENU_CONFIG = {
    "open_width": 150,  # Sidebar width when open (px)
    "closed_width": 0,  # Sidebar width when closed (px)
    "anim_duration": 300,  # Animation duration (ms)
    "anim_curve": QEasingCurve.Type.InOutCubic,  # Easing: smooth in/out instead of linear
    # Easing curve = how the speed changes during animation
    # Try swapping this for different effects:
    #   - QEasingCurve.InOutCubic  (smooth in & out)
    #   - QEasingCurve.OutBounce   (fun bounce at end)
    #   - QEasingCurve.InOutBack   (overshoot, then settle)
    #   - QEasingCurve.OutElastic  (springy / elastic effect)
    #   - QEasingCurve.Linear      (constant speed)
}

END_MARKER = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"


def resource_path(relative_path):
    # Get the directory of the current file (module)
    module_dir = dirname(abspath(__file__))

    return join(module_dir, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Start sidebar open
        self.menu_is_open = True

        self.id_input = 1

        self._load_ui()
        self._setup_sidebar()

    def _get_client_list(self):
        client_list: QTextEdit = self.findChild(QTextEdit, "client_list")
        show_clients_list(client_list)

    def _stop_server(self):
        server_output: QTextEdit = self.findChild(QTextEdit, "server_output")
        server_output.setText("")
        disconnect()

    def _update_settings(self):
        ip_setting: (QLineEdit, str) = self.findChild(QLineEdit, "ip_setting").text()
        port_setting: (QLineEdit, str) = self.findChild(
            QLineEdit, "port_setting"
        ).text()
        ip_type_setting: (QLineEdit, str) = self.findChild(
            QLineEdit, "ip_type_setting"
        ).text()
        username_setting: (QLineEdit, str) = self.findChild(
            QLineEdit, "user_setting"
        ).text()

        write_save_data(ip_setting, port_setting, ip_type_setting, username_setting)

    def _run_command(self):
        server_text = get_server_data()
        command_line_txt: QLineEdit = self.findChild(QLineEdit, "command_line_txt")
        command = command_line_txt.text()
        choice: [str, QLineEdit] = self.findChild(QLineEdit, "send_type_text").text()
        process_command(self, server_text, command, choice)

    def _load_ui(self):
        def _create_lessons():
            all_texts = (
                self.title_text,
                self.subtitle_text,
                self.points_text,
                self.desc_text,
                self.quiz_q_text,
                self.quiz_a_text,
            )
            data = create_json(self.id_input, all_texts)
            if data == "Halt":
                return

            if isinstance(data, int):
                self.id_input = data
            change_page(self, ui.lesson_editor, False)

        def _init_server():
            try:
                server_ip, server_port, ip_type = get_server_data()
            except TypeError as te:
                log_error(te)
                return

            start_server(server_ip, int(server_port), self, ip_type)

        def _list_lessons():
            change_page(self, ui.list_lessons_page, False)
            list_l_text: QLabel = self.findChild(QLabel, "list_l_text")
            lesson_data: str = list_lessons(
                error_message="Sorry! No locally stored lessons have been found!"
            )
            list_l_text.setText(lesson_data)

        def _show_edit_page():
            edit_id_text: QLineEdit = self.findChild(QLineEdit, "edit_id_text")
            try:
                id_num = int(edit_id_text.text())
            except Exception as e:
                log_error(e)
                edit_id_text.setText("Sorry! Unable to convert ID into number (int)!")
                print("Sorry! Unable to convert ID into number (int)!")
                return

            outcome = find_lesson(id_num)
            if outcome is None:
                edit_id_text.setText("Sorry! Unable to find lesson!")
                print("Sorry! Unable to find lesson!")
                return

            change_page(self, ui.edit_lesson_page, False)
            load_lesson_page(self, outcome)

        def _del_lesson():
            del_id_text: QLineEdit = self.findChild(QLineEdit, "del_id_text")
            try:
                id_num = int(del_id_text.text())
            except Exception as e:
                print(e)
                del_id_text.setText("Sorry! Unable to convert ID into number (int)!")
                return

            outcome = del_lesson(id_num)
            if outcome:
                del_id_text.setText(f"Deleted lesson with ID {id_num}")
                print(f"Deleted lesson with ID {id_num}")
            else:
                del_id_text.setText(f"Sorry! Failed to delete lesson!")
                print(f"Sorry! Failed to delete lesson!")

        def _get_lesson():
            get_l_id_text: QLineEdit = self.findChild(QLineEdit, "get_l_id_text")
            try:
                id_num = int(get_l_id_text.text())
            except Exception as e:
                log_error(e)
                get_l_id_text.setText(f"Sorry! Unable to convert ID into number (int)!")
                return

            outcome = find_lesson(id_num)
            if outcome is not None:
                get_l_id_text.setText("")
                change_page(self, ui.preview_l_page, False)
                init_lesson(self, outcome)
            else:
                get_l_id_text.setText(f"Sorry! Failed to preview lesson!")
                print(f"Sorry! Failed to preview lesson!")

        loader = QUiLoader()
        ui_file = QFile(resource_path("interface.ui"))
        ui_file.open(QFile.ReadOnly)
        ui = loader.load(ui_file, self)
        ui_file.close()

        if isinstance(ui, QMainWindow):
            self.setCentralWidget(ui.centralWidget())
        else:
            self.setCentralWidget(ui)

        # Find widgets and connect slots & signals
        (
            self.stacked_widget,
            self.side_menu,
            self.menu_btn,
            server_panel,
            create_lesson_page,
            self.title_text,
            self.points_text,
            self.subtitle_text,
            self.desc_text,
            self.quiz_a_text,
            self.quiz_q_text,
            create_lesson,
            list_l_button,
            del_l_button,
            get_l_p_button,
            edit_l_button,
            create_lesson_b_2,
            start_server_b,
            stop_server_b,
            run_cmd,
            refresh_c_list,
        ) = get_widgets(self, ui)
        submit_settings_b: QPushButton = self.findChild(QPushButton, "submit_settings")

        create_lesson.clicked.connect(_create_lessons)
        list_l_button.clicked.connect(_list_lessons)
        del_l_button.clicked.connect(_del_lesson)
        get_l_p_button.clicked.connect(_get_lesson)
        edit_l_button.clicked.connect(_show_edit_page)
        create_lesson_b_2.clicked.connect(lambda: edit_lesson(self, ui))

        start_server_b.clicked.connect(_init_server)
        stop_server_b.clicked.connect(self._stop_server)
        run_cmd.clicked.connect(self._run_command)
        refresh_c_list.clicked.connect(self._get_client_list)
        submit_settings_b.clicked.connect(self._update_settings)

        # Set home page
        change_page(self, ui.home_page, False, ui_name="home_page")

    def _setup_sidebar(self):
        self.side_menu.setMinimumWidth(MENU_CONFIG["closed_width"])
        self.side_menu.setMaximumWidth(MENU_CONFIG["open_width"])

        self.menu_btn.clicked.connect(self.toggle_menu)

    def toggle_menu(self):
        start = self.side_menu.width()
        end = (
            MENU_CONFIG["closed_width"]
            if self.menu_is_open
            else MENU_CONFIG["open_width"]
        )
        self.menu_is_open = not self.menu_is_open
        self._animate_width(start, end)

    def _animate_width(self, start, end):
        a_min = QPropertyAnimation(self.side_menu, b"minimumWidth")
        a_max = QPropertyAnimation(self.side_menu, b"maximumWidth")
        for anim in (a_min, a_max):
            anim.setDuration(MENU_CONFIG["anim_duration"])
            anim.setStartValue(start)
            anim.setEndValue(end)
            anim.setEasingCurve(MENU_CONFIG["anim_curve"])  # Set easing curve

        anim_group = QParallelAnimationGroup(self)
        anim_group.addAnimation(a_min)
        anim_group.addAnimation(a_max)
        anim_group.start()
