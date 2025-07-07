from os import system

print(system('pyinstaller --onedir --windowed ./server/lesson-editor.py'))
print(system('pyinstaller --onefile ./server/server.py'))
print(system('pyinstaller --onedir --windowed ./client/client.py'))

from shutil import copy2

source_path = 'LICENSE'
destination_path = 'dist/client/LICENSE'

try:
    copy2(source_path, destination_path)
except Exception:
    pass

source_path = 'LICENSE'
destination_path = 'dist/server/LICENSE'

try:
    copy2(source_path, destination_path)
except Exception:
    pass

source_path = 'LICENSE'
destination_path = 'dist/lesson-editor/LICENSE'

try:
    copy2(source_path, destination_path)
except Exception:
    pass