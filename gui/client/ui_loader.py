import sys

from time import sleep
from os.path import abspath, join
from threading import Thread

from PySide6.QtWidgets import QMainWindow, QPushButton, QLineEdit
from PySide6.QtCore import (
    QFile,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
)
from PySide6.QtUiTools import QUiLoader

from network.client import connectmod
from utils.client.paths import get_appdata_path
from utils.client.storage import write_save_data, import_file
from utils.crypto import decrypt_file, encrypt_file
from .widget_loader import get_widgets, change_page
from .lesson_page import init_lesson_page

# Loads all icons
import gui.client.icons_loader

# ----- CONFIG -----
MENU_CONFIG = {
    "open_width": 150,  # Sidebar width when open (px)
    "closed_width": 0,  # Sidebar width when closed (px)
    "anim_duration": 300,  # Animation duration (ms)
    "anim_curve": QEasingCurve.Type.InOutCubic,  # Easing: smooth in/out instead of linear
    # Easing curve = how the speed changes during animation
    # Try swapping this for different effects:
    #   - QEasingCurve.Type.InOutCubic  (smooth in & out)
    #   - QEasingCurve.Type.OutBounce   (fun bounce at end)
    #   - QEasingCurve.Type.InOutBack   (overshoot, then settle)
    #   - QEasingCurve.Type.OutElastic  (springy / elastic effect)
    #   - QEasingCurve.Type.Linear      (constant speed)
}

END_MARKER = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath(".")
    print(join(base_path, relative_path))
    return join(base_path, relative_path)


# --------------------------------------------------------------------------------------------------
# Network startup


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
        SERVER_IP = str(data[2])
        IP_TYPE = str(data[1])
        SERVER_PORT = int(data[0])

    Thread(
        target=attempt_connect_loop, args=(SERVER_IP, SERVER_PORT, IP_TYPE), daemon=True
    ).start()

except FileNotFoundError as fe:
    print(f"[!!] Connect data not found!\n{fe}")

except (ValueError, TypeError, IndexError) as ve:
    print(f"[!!] Corrupted data!\n{ve}")
    print(data)
    file_path = join(get_appdata_path(), "connect-data.txt")
    with open(file_path, "wb") as file:
        file.write(encrypt_file(""))

# --------------------------------------------------------------------------------------------------


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Start sidebar open
        self.menu_is_open = True

        self.id_input = 1
        self.page = 1
        self.leaderboard_page = 1
        self.leaderboard_type = "points"
        self.lesson_attempt = 1

        self._load_ui()
        self._setup_sidebar()

    def _show_lesson_page(self, ui, change_menu=True):
        change_page(self, ui.lessons_page, change_menu=change_menu)
        previous_page, next_page, total_pages = init_lesson_page(self, ui)

        # Disconnect all slots from this button's clicked signal
        try:
            previous_page.clicked.disconnect()
        except Exception:
            pass  # No connections yet

        # Disconnect all slots from this button's clicked signal
        try:
            next_page.clicked.disconnect()
        except Exception:
            pass  # No connections yet

        previous_page.clicked.connect(lambda: self.previous_page_set(ui))
        next_page.clicked.connect(lambda: self.next_page_set(ui, total_pages))

    def next_page_set(self, ui, total_page: int):
        if self.page >= total_page:
            return
        print(self.page)
        print(total_page)
        self.page += 1
        self._show_lesson_page(ui, change_menu=False)

    def previous_page_set(self, ui):
        if self.page <= 1:
            return
        print(self.page)
        self.page -= 1
        self._show_lesson_page(ui, change_menu=False)

    def _update_settings(self):
        ip_setting: str = self.findChild(QLineEdit, "ip_setting").text()
        port_setting: str = self.findChild(QLineEdit, "port_setting").text()
        ip_type_setting: str = self.findChild(QLineEdit, "ip_type_setting").text()
        username_setting: str = self.findChild(QLineEdit, "user_setting").text()
        if ip_type_setting == "":
            ip_type_setting = "ipv4"

        write_save_data(ip_setting, port_setting, ip_type_setting, username_setting)

    def _load_ui(self):

        loader = QUiLoader()
        ui_file = QFile(resource_path(join("gui", "client", "interface.ui")))
        ui_file.open(QFile.ReadOnly)
        ui = loader.load(ui_file, self)
        ui_file.close()

        if isinstance(ui, QMainWindow):
            self.setCentralWidget(ui.centralWidget())
        else:
            self.setCentralWidget(ui)

        (
            self.stacked_widget,
            self.side_menu,
            self.menu_btn,
            lesson_page,
            import_lessons_b,
        ) = get_widgets(self, ui)

        lesson_page.clicked.connect(lambda: self._show_lesson_page(ui))
        import_lessons_b.clicked.connect(lambda: import_file(self))

        self.findChild(QPushButton, "reload_lessons").clicked.connect(
            lambda: self._show_lesson_page(ui, False)
        )
        self.findChild(QPushButton, "submit_settings").clicked.connect(
            self._update_settings
        )
        # Set home page
        change_page(self, ui.home_page, change_menu=False, ui_name="home_page")

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
