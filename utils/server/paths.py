from os import getenv, makedirs
from os.path import exists as os_path_exists, expanduser, join
from platform import system


# Gets the full path to APPDATA.
def get_appdata_path():
    user_os = system()
    if user_os == "Windows":
        path_to_appdata = getenv("APPDATA")
    elif user_os == "Darwin":
        path_to_appdata = expanduser("~/Library/Application Support")
    else:
        path_to_appdata = getenv("XDG_DATA_HOME", expanduser("~/.local/share"))

    if os_path_exists(join(path_to_appdata, "PyEducate")):
        if os_path_exists((join(path_to_appdata, "PyEducate", "server"))):
            full_path_data = join(path_to_appdata, "PyEducate", "server")
        else:
            full_path_data = join(path_to_appdata, "PyEducate", "server")
            makedirs(full_path_data)
    else:
        makedirs(join(path_to_appdata, "PyEducate"))
        makedirs(join(path_to_appdata, "PyEducate", "server"))
        full_path_data = join(path_to_appdata, "PyEducate", "server")

    return full_path_data
