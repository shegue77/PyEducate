from os import system
from os.path import join
from shutil import copy2, copytree

stuff = ("LICENSE", "SOURCE")
dist_parts = ("client", "server", "server-cli")

server_cli = "server-cli.py"
server_path = "server.py"
client_path = "client.py"

print(system(f"pyinstaller --windowed {server_path}"))
print(system(f"pyinstaller {server_cli}"))
print(system(f"pyinstaller --windowed {client_path}"))

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
