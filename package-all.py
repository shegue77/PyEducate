from os import system
from os.path import join
from shutil import copy2, copytree

stuff = ("LICENSE", "SOURCE")
dist_parts = ("client", "server", "lesson-editor")

lesson_edit_path = join('server', 'lesson-editor.py')
server_path = join('server', 'server.py')
client_path = join('client', 'client.py')
print(system(f"pyinstaller --onedir --windowed {lesson_edit_path}"))
print(system(f"pyinstaller --onefile {server_path}"))
print(system(f"pyinstaller --onedir --windowed {client_path}"))

for part in dist_parts:
    for i in stuff:
        source_path = str(i)
        destination_path = join("dist", str(part), str(i))

        try:
            copy2(source_path, destination_path)
        except Exception:
            pass

    destination_path = join("dist", str(part), "THIRD-PARTY-LICENSES")
    try:
        copytree('THIRD-PARTY-LICENSES', destination_path)
    except Exception:
        pass