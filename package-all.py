from os import system

stuff = ('LICENSE', 'CREDITS')

print(system('pyinstaller --onedir --windowed ./server/lesson-editor.py'))
print(system('pyinstaller --onefile ./server/server.py'))
print(system('pyinstaller --onedir --windowed ./client/client.py'))

from shutil import copy2

for i in range(2):
    source_path = str(stuff[i])
    destination_path = f'dist/client/{stuff[i]}'

    try:
        copy2(source_path, destination_path)
    except Exception:
        pass

for i in range(2):
    source_path = str(stuff[i])
    destination_path = f'dist/server/{stuff[i]}'

    try:
        copy2(source_path, destination_path)
    except Exception:
        pass

for i in range(2):
    source_path = str(stuff[i])
    destination_path = f'dist/lesson-editor/{stuff[i]}'

    try:
        copy2(source_path, destination_path)
    except Exception:
        pass