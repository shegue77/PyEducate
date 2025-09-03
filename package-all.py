from os import system
from os.path import join
from shutil import copy2, copytree

stuff = ("LICENSE", "SOURCE")
dist_parts = ("client", "server")

server_path = "server.py"
client_path = "client.py"

print(
    system(f'pyinstaller {server_path} --windowed --add-data "gui/server;gui/server" --add-data "site/*;site"')
)
print(
    system(f'pyinstaller {client_path} --windowed --add-data "gui/client;gui/client" --add-data "site/*;site"')
)

for part in dist_parts:
    for i in stuff:
        source_path = str(i)
        destination_path = join("dist", str(part), str(i + ".txt"))

        try:
            copy2(source_path, destination_path)
        except Exception:
            pass

    destination_path = join("dist", str(part), "THIRD-PARTY-LICENSES")
    try:
        copytree("THIRD-PARTY-LICENSES", destination_path)
    except Exception:
        pass
