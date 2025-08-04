from datetime import datetime
from os.path import join
from .paths import get_appdata_path


def log_error(data):

    # Get current time
    now = datetime.now()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    log_path = str(join(get_appdata_path(), "server.log"))

    data = str(timestamp + " " + str(data) + "\n")

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(data)

    except FileNotFoundError:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(data)

    except PermissionError:
        print(f"[!] Insufficient permissions!\n" f"Unable to log data at {log_path}!")
