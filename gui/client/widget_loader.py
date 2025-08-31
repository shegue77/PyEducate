from json import JSONDecodeError
from os.path import join, exists

from utils.client.paths import get_appdata_path
from utils.client.logger import log_error
from utils.client.storage import get_username, write_json, load_json
from utils.crypto import decrypt_file
from .lesson_page import get_points_data

from PySide6.QtWidgets import QStackedWidget, QFrame, QPushButton, QLineEdit, QLabel


def init_leaderboard(self):
    def read_leaderboard(filename):
        if not exists(filename):
            # Create empty file if it doesn't exist
            write_json(filename, [])
            return []

        try:
            json_data = load_json(filename)
            return json_data
        except Exception as e:
            log_error(e)
            return []

    def get_top_n_users(filename, type_n="points", n=10):
        leaderboard = read_leaderboard(filename)
        # Sort by points descending
        sorted_leaderboard = sorted(leaderboard, key=lambda x: x[type_n], reverse=True)
        return sorted_leaderboard[:n]

    def get_total_pages():
        file_path = join(get_appdata_path(), "leaderboards.json")

        def create_json():
            json_data = []
            write_json(file_path, json_data)

        try:
            data = load_json(file_path)

        except (FileNotFoundError, JSONDecodeError) as fe:
            log_error(fe)
            create_json()
            data = []

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
        init_leaderboard(self)
        return None

    def previous_page_set():
        if self.leaderboard_page <= 1:
            return None

        self.leaderboard_page -= 1
        init_leaderboard(self)
        return None

    def get_board_type():
        board_types = get_total_pages()[0]
        try:
            self.leaderboard_type = str(board_types[self.leaderboard_page - 1])
        except IndexError as ie:
            log_error(ie)
            print(ie)
            # self.show_message_box(
            #    "error",
            #    "Leaderboard",
            #    "Unable to initialise the leaderboard!\n"
            #    "This is due to no known players being on the leaderboard.",
            # )
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

    self.findChild(QLabel, "leader_subtitle").setText(
        f"Top 10 by {str(self.leaderboard_type).replace('_', ' ').lower().capitalize()}"
    )

    data = get_top_n_users(
        join(get_appdata_path(), "leaderboards.json"),
        str(self.leaderboard_type),
        10,
    )

    for idx, part in enumerate(data, start=1):
        try:
            badge = badge_for_ranking[idx]
        except IndexError:
            badge = " "

        self.findChild(QLabel, f"lead_{idx}").setText(
            f'{badge} {idx}. Username: {part["username"]}  |  '
            f"{str(self.leaderboard_type).strip().replace('_', ' ').lower().capitalize()}: "
            f"{part[str(self.leaderboard_type.strip())]:,.2f}"
        )

    self.findChild(QLabel, "lead_total_pages").setText(
        f"Page: {self.leaderboard_page}/{total_pages}"
    )

    previous_page = self.findChild(QPushButton, "previous_page_lead")
    next_page = self.findChild(QPushButton, "next_page_lead")

    if self.leaderboard_page >= total_pages:
        next_page.setDisabled(True)
    else:
        next_page.setDisabled(False)

    if self.leaderboard_page <= 1:
        previous_page.setDisabled(True)
    else:
        previous_page.setDisabled(False)

    previous_page.clicked.connect(previous_page_set)
    next_page.clicked.connect(lambda: next_page_set(total_pages))
    return None


def _load_settings_page(self):
    full_path = get_appdata_path()
    try:
        with open(join(full_path, "connect-data.txt"), "rb") as f:
            data = decrypt_file(f.read()).strip().split()
            try:
                server_port = data[0]
            except IndexError as ie:
                log_error(ie)
                server_port = ""
            try:
                ip_type = data[1]
            except IndexError as ie:
                log_error(ie)
                ip_type = ""
            try:
                server_ip = data[2]
            except IndexError as ie:
                log_error(ie)
                server_ip = ""
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

    points, lessons_completed = get_points_data()

    self.findChild(QLineEdit, "ip_setting").setText(str(server_ip))
    self.findChild(QLineEdit, "port_setting").setText(str(server_port))
    self.findChild(QLineEdit, "ip_type_setting").setText(str(ip_type))
    self.findChild(QLineEdit, "user_setting").setText(username)
    self.findChild(QLabel, "points_amount").setText(f"Points: {points:,.2f}")
    self.findChild(QLabel, "lescomplete_amount").setText(
        f"Lessons completed: {lessons_completed:,}"
    )


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
                        "Welcome to PyEducate! We're excited to have you! Let's get started!"
                    )

            except FileNotFoundError:
                home_text.setText(
                    "Welcome to PyEducate! We're excited to have you! Let's get started!"
                )
        elif ui_name == "leaderboard_page":
            init_leaderboard(self)


def get_widgets(self, ui):
    stacked_widget = self.findChild(QStackedWidget, "stackedWidget")
    side_menu = self.findChild(QFrame, "side_menu")
    menu_btn = self.findChild(QPushButton, "pushButton")

    # Load & connect menu buttons
    lesson_page = self.findChild(QPushButton, "lessons_button")
    import_lessons_b: QPushButton = self.findChild(QPushButton, "import_lessons_b")
    self.findChild(QPushButton, "home_button").clicked.connect(
        lambda: change_page(self, ui.home_page, ui_name="home_page")
    )
    self.findChild(QPushButton, "leaderboard_button").clicked.connect(
        lambda: change_page(self, ui.leaderboard_page, ui_name="leaderboard_page")
    )
    self.findChild(QPushButton, "settings_button").clicked.connect(
        lambda: change_page(self, ui.settings_page, ui_name="settings_page")
    )
    self.findChild(QPushButton, "about_button").clicked.connect(
        lambda: change_page(self, ui.about_page)
    )

    return (stacked_widget, side_menu, menu_btn, lesson_page, import_lessons_b)
