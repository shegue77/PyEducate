
# ---------------------------[ DEPENDENCIES ]---------------------------
import socket
from threading import Thread, Lock
from json import load, loads, dump, dumps, JSONDecodeError
from os import getenv, makedirs
from datetime import datetime
from os.path import exists as os_path_exists
from schedule import every, run_pending
# ----------------------------------------------------------------------


# -------------------------[ GLOBAL VARIABLES ]-------------------------
clients = {}    # Keeps track of clients
usernames = {}  # Keeps track of usernames of clients
active_threads = [] # Keeps track of (most) active threads.
end_marker = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"  # End marker used when sending JSON files, make sure this does NOT appear at all in your JSON file.
# MAKE SURE that this end marker MATCHES the end marker on the client.
safe_leaderboard = Lock()
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

def log_error(data):

    # Get current time
    now = datetime.now()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    log_path = str(get_appdata_path() + '\\server.log')

    data = str(timestamp + ' ' + str(data) + '\n')

    try:
        with open(log_path, 'a') as f:
            f.write(data)

    except FileNotFoundError:
        with open(log_path, 'w') as f:
            f.write(data)

    except PermissionError:
        print(f'[!] Insufficient permissions!\nUnable to log data at {log_path}!')

# Parses and sends the JSON file to the client.
def send_json(client, file_path, id_n=None):

    try:
        file = open(file_path, 'r', encoding='utf-8')
    except FileNotFoundError:
        file_path = str(get_appdata_path()+ '\\lessons.json')
        file = open(file_path, 'r', encoding='utf-8')

    full_data = file.read()

    try:
        loads(full_data)
    except Exception as e:
        print("[!] INVALID JSON! Sending failed!")
        print(e)
        log_error(e)
        return

    data = loads(full_data)

    if id_n is None:
        sending_data = dumps(data.get("lessons", []))

    else:
        id_n = list(id_n)
        sending_data = []

        for id_s in id_n:
            id_found = False
            for lesson in data['lessons']:
                if int(lesson['id']) == int(id_s):
                    sending_data.append(lesson)
                    id_found = True
                    break

            if not id_found:
                print(f'ID {id_s} not found in {file_path}!')

        sending_data = dumps(sending_data)

    client.sendall(sending_data.encode())

    if end_marker in sending_data.encode():
        print(f"[!] END MARKER FOUND IN {file_path}, SENDING POTENTIALLY CORRUPTED DATA.")

    client.sendall(bytes(end_marker))

    file.close()

def send_leaderboard(client, filename):

    try:
        file = open(filename, 'r', encoding='utf-8')
    except FileNotFoundError:
        filename = str(get_appdata_path() + '\\leaderboard.json')
        file = open(filename, 'r', encoding='utf-8')

    file.close()
    full_data = str(clean_leaderboard(filename))

    try:
        loads(full_data)
    except Exception as e:
        print("[!] INVALID JSON! Sending failed!")
        print(e)
        log_error(e)
        return

    data = loads(full_data)
    data = dumps(data)


    client.sendall(data.encode())

    if end_marker in data.encode():
        print(f"[!] END MARKER FOUND IN {filename}, SENDING POTENTIALLY CORRUPTED DATA.")

    client.sendall(bytes(end_marker))

# Load the leaderboard from the JSON file
def read_leaderboard(filename):
    with safe_leaderboard:
        if not os_path_exists(filename):
            # Create empty file if it doesn't exist
            with open(filename, 'w') as f:
                dump([], f)
            return []

        with open(filename, 'r') as f:
            return load(f)

def clean_leaderboard(file_path):
    def get_top_n_users(filename, n=10, type_n='points'):
        leaderboard = read_leaderboard(filename)
        # Sort by points descending
        sorted_leaderboard = sorted(leaderboard, key=lambda x: x[type_n], reverse=True)
        return sorted_leaderboard[:n]

    def get_board_types(file_path):

        def create_json():
            with open(file_path, 'w', encoding="utf-8") as file:
                json_data = []
                dump(json_data, file, indent=4)

        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                data = load(f)

        except FileNotFoundError as fe:
            log_error(fe)
            create_json()

        except JSONDecodeError:
            with open(file_path, 'w', encoding="utf-8") as file:
                data = []
                dump(data, file)

        leaderboard_items = []

        for part in data:
            for i in part.keys():
                if i != 'username':
                    leaderboard_items.append(i)
            break

        return leaderboard_items

    file_data_types = get_board_types(file_path)
    file_data = []
    for part in file_data_types:
        board_items = get_top_n_users(file_path, 10, str(part))
        for person in board_items:
            found = False
            for file_part in file_data:
                if person["username"] == file_part["username"]:
                    found = True
                    break

            if not found:
                file_data.append(person)

    print(dumps(file_data))
    return dumps(file_data)


def update_leaderboard(username, point_amount, lesson_completed):
    FILENAME = str(get_appdata_path()) + '\\leaderboard.json'

    # Save the leaderboard to the JSON file
    def write_leaderboard(filename, leaderboard):
        with safe_leaderboard:
            with open(filename, 'w') as f:
                dump(leaderboard, f, indent=4)

    # Add or update a user in the leaderboard
    def add_or_update_user(filename, user, points, lessons_completed):
        leaderboard = read_leaderboard(filename)
        found = False

        for entry in leaderboard:
            if entry['username'] == user:
                entry['points'] = points
                entry['lessons_completed'] = lessons_completed
                found = True
                break

        if not found:
            leaderboard.append({
                "username": user,
                "points": points,
                "lessons_completed": lessons_completed
            })

        write_leaderboard(filename, leaderboard)

    if username == 'Unknown':
        return None

    add_or_update_user(FILENAME, username, point_amount, lesson_completed)

# Function to handle each connected client
def handle_client(client_socket, addr):
    clients[addr] = client_socket
    print(f"[!] {addr[0]} connected.")

    try:
        client_socket.sendall('!getusername'.encode())
    except Exception as er:
        log_error(er)

    while True:
        try:
            response = client_socket.recv(4096).decode().strip().lower()
            if not response:
                break

            if str(response).startswith('!getusername'):
                username = response.split(" ")[1].strip()
                usernames[addr] = username

            elif str(response).startswith('!getstats'):
                points = int(response.split(" ")[1])
                lessons_completed = int(response.split(" ")[2])
                username = usernames.get(addr, 'Unknown')

                update_leaderboard(username, points, lessons_completed)

            else:
                print(f"\n[{addr[0]} Output]: {response}")

        except (ConnectionResetError, BrokenPipeError):
            break

    print(f"[!] Client {addr[0]} disconnected.")
    client_socket.close()
    del clients[addr]
    usernames.pop(addr, None)

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
        
    !gethostname
        Gets the hostname of client(s).
        
    !getusername
        Gets the username of client(s).
        
    !getstats
        Gets leaderboard data of client(s), used to update their leaderboard.
    
    !updateboard [path]
        Parses and sends leaderboard data of the top 10 which is in a leaderboard JSON to client(s).
        Example: !updateboard leaderboard.json
        
    !sendlesson <lesson_ID> [path]
        Sends specific lesson(s) from a JSON file containing lessons (identified by ID) to client(s).
        Example 1: !sendlesson [2] lessons.json
        Example 2: !sendlesson [1, 3, 4] lessons.json
    
    !sendjson [path]
        Sends a JSON file containing ALL lessons to client(s).
        Example: !sendjson lessons.json
    
    !disconnect
        Cuts a connection with client(s).
    
    !shutdown
        Safely disconnects all clients before shutting down the server.
        Use with caution.
        
Notes:
- Arguments in <> are required.
- Arguments in [] are optional.
- To refresh client list & command prompt, press the 'enter' key.
    
    """
    return data

# Starts the server and listens for clients.
def start_server(host, port, server_type='ipv4', marker_end=b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"):

    if server_type == 'ipv6':
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((host, port))
    server.listen()
    print("\n\nPyEducate: Teacher Panel")
    print("Made by shegue77, see license and source code at the github repo: https://github.com/shegue77/PyEducate")
    print("Press the 'enter' key to refresh client list & the command prompt.\n")
    print("For more help about the commands of this tool, run !help to view all commands with explanations.\n")
    print(f"[*] Listening on {host}:{port}")

    # Start accepting client connections

    Thread(target=accept_clients, args=(server,), daemon=True).start()

    print("Waiting for clients to connect...")

    data = (host, port, server_type, marker_end)
    every(30).seconds.do(lambda: print("Waiting for clients to connect..."))
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
            username = usernames.get(addr, "Unknown")
            print(f"{idx}. {addr[0]} - {username}")

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
            command = input("Enter command to send (broadcast): ").strip().lower()

            if command.startswith("!help") or command.startswith("help"):
                print(help_data())
                continue

            if not command.startswith("!sendjson") and not command.startswith("!shutdown") and not command == '' and not command.startswith("!updateboard"):
                for client in clients.values():
                    client.sendall(command.encode())

            elif command.startswith("!shutdown"):
                disconnect(clients.values(), server)

            elif command.startswith("!info"):
                print(f"SERVER IP: {server_data[0]}\nSERVER PORT: {server_data[1]}\nIP TYPE: {server_data[2]}\nEnd marker: {str(server_data[3])}\n")

            elif command == "":
                continue

            if command.startswith("!updateboard"):
                for client in clients.values():
                    try:
                        file_path_json = command.split(" ")[1]

                    except IndexError:
                        file_path_json = get_appdata_path() + '\\leaderboard.json'

                    except Exception as er:
                        file_path_json = get_appdata_path() + '\\leaderboard.json'
                        log_error(er)

                    client.sendall(str('!updateboard').encode())

                    thread = Thread(target=send_leaderboard, args=(client, file_path_json))

                    thread.start()
                    active_threads.append(thread)

            if command.startswith("!sendjson") or command.startswith("!sendlesson"):
                for client in clients.values():
                    if command.startswith("!sendjson"):
                        try:
                            file_path_json = command.split(" ")[1]

                        except IndexError:
                            file_path_json = get_appdata_path() + '\\lessons.json'

                        except Exception as er:
                            file_path_json = get_appdata_path() + '\\lessons.json'
                            log_error(er)


                    else:
                        try:
                            lesson_id = command.replace(']', '[').split("[")[1]
                            lesson_id = lesson_id.replace(',', '').split(' ')

                        except Exception as ie:
                            log_error(ie)
                            print('[!] LESSON ID NOT SPECIFIED!')
                            continue

                        try:
                            file_path_json = command.split("] ")[-1]

                        except IndexError:
                            file_path_json = get_appdata_path() + '\\lessons.json'

                        except Exception as er:
                            file_path_json = get_appdata_path() + '\\lessons.json'
                            log_error(er)

                    client.sendall(str('!sendjson').encode())

                    if command.startswith("!sendjson"):
                        thread = Thread(target=send_json, args=(client, file_path_json))
                    else:
                        thread = Thread(target=send_json, args=(client, file_path_json, lesson_id))

                    thread.start()
                    active_threads.append(thread)

        elif 0 <= choice < len(clients):
            target_addr = list(clients.keys())[choice]
            command = input(f"Enter command to send to {target_addr[0]}: ").strip().lower()

            if command.startswith("!sendjson") or command.startswith("!sendlesson"):
                if command.startswith("!sendjson"):
                    try:
                        file_path_json = command.split(" ")[1]

                    except IndexError:
                        file_path_json = get_appdata_path() + '\\lessons.json'

                    except Exception as er:
                        file_path_json = get_appdata_path() + '\\lessons.json'
                        log_error(er)


                else:
                    try:
                        lesson_id = command.replace(']', '[').split("[")[1]
                        lesson_id = lesson_id.replace(',', '').split(' ')
                        print(lesson_id)

                    except Exception as ie:
                        log_error(ie)
                        print('[!] LESSON ID NOT SPECIFIED!')
                        continue

                    try:
                        file_path_json = command.split("] ")[-1]

                    except IndexError:
                        file_path_json = get_appdata_path() + '\\lessons.json'

                    except Exception as er:
                        file_path_json = get_appdata_path() + '\\lessons.json'
                        log_error(er)

                clients[target_addr].sendall(str('!sendjson').encode())

                if command.startswith("!sendjson"):
                    thread = Thread(target=send_json, args=(clients[target_addr], file_path_json))
                else:
                    thread = Thread(target=send_json, args=(clients[target_addr], file_path_json, lesson_id))

                thread.start()
                active_threads.append(thread)

            elif command.startswith("!updateboard"):
                try:
                    file_path_json = command.split(" ")[1]

                except IndexError:
                    file_path_json = get_appdata_path() + '\\leaderboard.json'

                except Exception as er:
                    file_path_json = get_appdata_path() + '\\leaderboard.json'
                    log_error(er)

                clients[target_addr].sendall(str('!sendjson').encode())

                thread = Thread(target=send_leaderboard, args=(clients[target_addr], file_path_json))

                thread.start()
                active_threads.append(thread)

            elif command == "":
                continue

            elif command.startswith("!help"):
                print(help_data())

            elif command.startswith("!info"):
                print(f"SERVER IP: {server_data[0]}\nSERVER PORT: {server_data[1]}\nIP TYPE: {server_data[2]}\nEnd marker: {str(server_data[3])}\n")

            elif command.startswith("!shutdown"):
                print("[!] Unsupported command, please use broadcast to run !shutdown.\nDid you mean !exit?")

            else:
                clients[target_addr].sendall(command.encode())


        else:
            print("[!] Invalid selection.")


# Reads the data about the IP, PORT and IP TYPE (IPv4/IPv6) of the server and connects to the server.
if __name__ == "__main__":
    full_path = get_appdata_path()
    ANSWER = str(input('Would you like to change any settings (y/n): ')).strip().lower()
    if ANSWER == 'y' or ANSWER == 'yes':
        SERVER_IP = str(input("Enter server IP (IPv4/IPv6): "))
        SERVER_PORT = int(input("Enter server port: "))
        IP_TYPE = str(input("Enter IP type (IPv4/IPv6): ")).lower()
        end_marker = input("Enter the end marker if desired (Must match with client. End marker has a default preset): ")
        with open(full_path + '\\connect-data.txt', 'w', encoding='utf-8') as f:
            f.write(f"{SERVER_IP}\n{SERVER_PORT}\n{IP_TYPE}\n{end_marker}")

    try:
        with open(full_path + '\\connect-data.txt', 'r', encoding='utf-8') as f:
            SERVER_IP = str(f.readline().strip().replace('\n', ''))
            SERVER_PORT = int(f.readline().strip().replace(' ', ''))
            try:
                IP_TYPE = str(f.readline().strip()).lower()

            except Exception as e:
                print('[!] Unable to extract IP type (IPv4/IPv6), defaulting to IPv4...')
                IP_TYPE = "ipv4"
                log_error(e)

            try:
                end_marker = f.readline().strip().encode()
                if end_marker.strip() == b'':
                    end_marker = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"
            except Exception as e:
                log_error(e)
                end_marker = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"

    except FileNotFoundError as fe:
        log_error(fe)
        print('[!] Unable to locate save data!\n')
        SERVER_IP = str(input("Enter server IP (local): "))
        SERVER_PORT = int(input("Enter server port: "))
        IP_TYPE = str(input("Enter IP type (IPv4/IPv6): ")).lower()
        end_marker = input("Enter the end marker if desired (Must match with client. Enter nothing if unsure): ").encode()
        try:
            if end_marker.strip() == b'':
                end_marker = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"

        except Exception as e:
            end_marker = b"<<<<<<<erjriefjgjrffjdgo>>>>>>>>>>"
            log_error(e)


        with open(full_path + '\\connect-data.txt', 'w', encoding='utf-8') as f:
            f.write(f"{SERVER_IP}\n{SERVER_PORT}\n{IP_TYPE}\n{end_marker}")

    start_server(SERVER_IP, SERVER_PORT, IP_TYPE, end_marker)