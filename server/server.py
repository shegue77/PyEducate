
# ---------------------------[ DEPENDENCIES ]---------------------------
import socket
from threading import Thread
from json import loads, dumps
from os import getenv, makedirs
from os.path import exists as os_path_exists
from schedule import every, run_pending
# ----------------------------------------------------------------------


# -------------------------[ GLOBAL VARIABLES ]-------------------------
clients = {}    # Keeps track of clients
active_threads = [] # Keeps track of (most) active threads.
end_marker = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"  # End marker used when sending JSON files, make sure this does NOT appear at all in your JSON file.
# MAKE SURE that this end marker MATCHES the end marker on the client.
# ----------------------------------------------------------------------


# Gets the full path to APPDATA.
def get_appdata_path():
    path_to_appdata = getenv('APPDATA')
    if os_path_exists(path_to_appdata + "\\PyEducate"):
        if os_path_exists(path_to_appdata + "\\PyEducate\\server"):
            full_path_data = path_to_appdata + "\\PyEducate\\server"
        else:
            makedirs(path_to_appdata + "\\PyEducate\\server")
            full_path_data = path_to_appdata + "\\PyEducate\\server"
    else:
        makedirs(path_to_appdata + "\\PyEducate")
        makedirs(path_to_appdata + "\\PyEducate\\server")
        full_path_data = path_to_appdata + "\\PyEducate\\server"

    return full_path_data

# Parses and sends the JSON file to the client.
def send_json(client, file_path):
    global end_marker

    print('Sending initiated')
    print('Got file size')
    file = open(file_path, 'r')
    full_data = file.read()

    try:
        loads(full_data)
    except Exception as e:
        print("WARNING! INVALID JSON")
        print(e)
        return

    data = loads(full_data)

    sending_data = dumps(data.get("lessons", []))

    client.sendall(sending_data.encode())

    if end_marker not in sending_data.encode():
        print("Sending end marker safely...")
    else:
        print(f"[!] END MARKER FOUND IN {file_path}, SENDING POTENTIALLY CORRUPTED DATA.")

    client.sendall(bytes(end_marker))

    file.close()

# Function to handle each connected client
def handle_client(client_socket, addr):
    clients[addr] = client_socket
    print(f"{addr[0]} connected.")

    while True:
        try:
            response = client_socket.recv(4096).decode()
            if not response:
                break
            print(f"\n[{addr[0]} Output]: {response}")

        except (ConnectionResetError, BrokenPipeError):
            break

    print(f"[!] Client {addr[0]} disconnected.")
    client_socket.close()
    del clients[addr]

# Function is used to safely shutdown the server. Is run when !shutdown is called.
def disconnect(clients_list, server_m):
    global active_threads

    if any(t.is_alive() for t in active_threads):
        print("[!] Potentially active threads detected. Please make sure all threads are closed to prevent critical data loss.\n(Note that this may be a false positive but please proceed with caution)\n")

        if str(input("[*] Would you like to continue the server shutdown - NOT RECOMMENDED (y/n): ")) == "y":
            print("[!!] Proceeding with potentially unsafe server shutdown...\n")

        else:
            print("Server shutdown safely aborted.\n")
            return

    else:
        if str(input("[*] No active threads detected. Would you like to continue the server shutdown (y/n): ")).strip().lower() == "y":
            print("\n[*] Shutting down server...")

        else:
            print("[*] Server shutdown safely aborted.\n")
            return

    active_threads = [t for t in active_threads if t.is_alive()]

    for client in clients_list:
        client.sendall("!disconnect".encode())
        client.close()

    server_m.close()
    exit(0)


# Displays help data for commands.
def help_data():
    data = """
    
Available Commands:
    
    !help
        Opens the help list.
    
    !info
        Shows information of the server.
    
    !getip
        Gets the public IPv4 address of client(s).
    
    !sendjson [path]
        Send a JSON file to client(s).
        Example: !sendjson lessons.json
    
    !disconnect
        Cuts a connection with client(s).
    
    !shutdown
        Safely disconnects all clients before shutting down the server.
        Use with caution.
        
Notes:
- Arguments in <> are required.
- Arguments in [] are optional.
- To refresh client list, press the 'enter' key.
  If there are no connected clients, the command prompt will seem to "freeze".
  However, this is normal and will "unfreeze" when at least one client is connected.
    
    """
    return data

# Starts the server and listens for clients.
def start_server(host, port, server_type='ipv4', marker_end=b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"):
    def print_client_wait():
        print("Waiting for clients to connect...")

    if server_type == 'ipv6':
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((host, port))
    server.listen()
    print("PyEducate: Teacher Panel v1.0")
    print("Made by shegue77, see license and source code at the github repo: https://github.com/shegue77/PyEducate")
    print("If client list is frozen, press the 'enter' key to unfreeze (may be stuck frozen if no clients are connected, resolves automatically).\n")
    print("For more help about the commands of this tool, run !help to view all commands with explanations.\n")
    print(f"[*] Listening on {host}:{port}")

    # Start accepting client connections

    Thread(target=accept_clients, args=(server,), daemon=True).start()

    print_client_wait()

    data = (host, port, server_type, marker_end)
    every(30).seconds.do(print_client_wait)
    process_commands(server, data)  # Start processing commands for the connected clients

# Function to accept incoming client connections
def accept_clients(server):
    while True:
        client_socket, addr = server.accept()
        Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

# Function to process commands and communicate with the client
def process_commands(server, server_data):
    global active_threads

    while True:
        if not clients:
            run_pending()
            continue

        print("\n[Connected Clients]")
        for idx, addr in enumerate(clients.keys(), start=1):
            print(f"{idx}. {addr[0]}")

        choice = input("Select client number (or 0 to broadcast): ")

        try:
            choice = int(choice) - 1
        except ValueError:
            if str(choice).strip().lower().startswith("!help") or str(choice).strip().lower().startswith("help"):
                print(help_data())
            elif str(choice).strip().lower().startswith("!info"):
                print(f"SERVER IP: {server_data[0]}\nSERVER PORT: {server_data[1]}\nIP TYPE: {server_data[2]}\nEnd marker: {str(server_data[3])}\n")
            continue

        if choice == -1:
            # Broadcast command to all clients
            command = input("Enter command to send (broadcast): ")

            if not command.strip().lower().startswith("!sendjson") and not command.strip().lower().startswith("!shutdown"):
                for client in clients.values():
                    client.sendall(command.encode())

            elif command.strip().lower().startswith("!shutdown"):
                disconnect(clients.values(), server)

            elif command.strip().lower().startswith("!info"):
                print(f"SERVER IP: {server_data[0]}\nSERVER PORT: {server_data[1]}\nIP TYPE: {server_data[2]}\nEnd marker: {str(server_data[3])}\n")

            elif command.strip() == "":
                continue

            elif command.strip().lower().startswith("!help") or command.strip().lower().startswith("help"):
                print(help_data())

            elif command.strip().lower().startswith("!sendjson"):
                for client in clients.values():
                    try:
                        file_path_json = command.split()[1]
                    except IndexError:
                        file_path_json = get_appdata_path() + '\\lessons.json'

                    command_part = command.split()[0]
                    client.sendall(str(command_part).encode())
                    thread = Thread(target=send_json, args=(client, file_path_json))
                    thread.start()
                    active_threads.append(thread)

                print('Sending data to all')

        elif 0 <= choice < len(clients):
            target_addr = list(clients.keys())[choice]
            command = input(f"Enter command to send to {target_addr[0]}: ")

            if command.strip().lower().startswith("!sendjson"):
                try:
                    file_path_json = command.strip().split()[1]
                except IndexError:
                    file_path_json = get_appdata_path() + '\\lessons.json'

                command_part = command.split()[0]
                clients[target_addr].sendall(str(command_part).encode())
                thread = Thread(target=send_json, args=(clients[target_addr], file_path_json))
                thread.start()
                active_threads.append(thread)

            elif command.strip() == "":
                continue

            elif command.strip().lower().startswith("!help"):
                print(help_data())

            elif command.strip().lower().startswith("!info"):
                print(f"SERVER IP: {server_data[0]}\nSERVER PORT: {server_data[1]}\nIP TYPE: {server_data[2]}\nEnd marker: {str(server_data[3])}\n")

            elif command.strip().lower().startswith("!shutdown"):
                print("[!] Unsupported command, please use broadcast to run !shutdown.\nDid you mean !exit?")

            else:
                clients[target_addr].sendall(command.encode())


        else:
            print("[!] Invalid selection.")


# Reads the data about the IP, PORT and IP TYPE (IPv4/IPv6) of the server and connects to the server.
if __name__ == "__main__":
    full_path = get_appdata_path()
    answer = str(input('Would you like to change any settings (y/n): ')).strip().lower()
    if answer == 'y' or answer == 'yes':
        SERVER_IP = str(input("Enter server IP (IPv4/IPv6): "))
        SERVER_PORT = int(input("Enter server port: "))
        IP_TYPE = str(input("Enter IP type (IPv4/IPv6): ")).lower()
        end_marker = input("Enter the end marker if desired (Must match with client. End marker has a default preset): ")
        with open(full_path + '\\connect-data.txt', 'w') as f:
            f.write(f"{SERVER_IP}\n{SERVER_PORT}\n{IP_TYPE}\n{end_marker}")

    try:
        with open(full_path + '\\connect-data.txt', 'r') as f:
            SERVER_IP = str(f.readline().strip().replace('\n', ''))
            SERVER_PORT = int(f.readline().strip().replace(' ', ''))
            try:
                IP_TYPE = str(f.readline().strip()).lower()
            except Exception:
                print('[!] Unable to extract IP type (IPv4/IPv6), defaulting to IPv4...')
                IP_TYPE = "ipv4"
            try:
                end_marker = bytes(f.readline().strip())
            except Exception:
                end_marker = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"

    except FileNotFoundError:
        print('[!] Unable to locate save data!\n')
        SERVER_IP = str(input("Enter server IP (IPv4/IPv6): "))
        SERVER_PORT = int(input("Enter server port: "))
        IP_TYPE = str(input("Enter IP type (IPv4/IPv6): ")).lower()
        end_marker = input("Enter the end marker if desired (Must match with client. End marker has a default preset): ")
        try:
            end_marker = bytes(end_marker)
        except Exception:
            end_marker = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"
        with open(full_path + '\\connect-data.txt', 'w') as f:
            f.write(f"{SERVER_IP}\n{SERVER_PORT}\n{IP_TYPE}\n{end_marker}")

    start_server(SERVER_IP, SERVER_PORT, IP_TYPE, end_marker)