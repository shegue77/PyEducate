import socket
import threading
import os

clients = {}

# Function to display the logo
def logo():
    print("PyEducate: Teacher Panel")

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

def start_server(host="127.0.0.1", port=34232, server_type='ipv4'):
    if server_type == 'ipv6':
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
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

# Function to process commands and communicate with the client
def process_commands():
    while True:
        if not clients:
            continue

        print("\n[Connected Clients]")
        for idx, addr in enumerate(clients.keys(), start=1):
            print(f"{idx}. {addr[0]}")
            print(addr)

        try:
            choice = int(input("Select client number (or 0 to broadcast): ")) - 1
        except ValueError:
            continue

        if choice == -1:
            # Broadcast command to all clients
            command = input("Enter command to send (broadcast): ")
            for client in clients.values():
                client.sendall(command.encode())

        elif 0 <= choice < len(clients):
            target_addr = list(clients.keys())[choice]
            command = input(f"Enter command to send to {target_addr[0]}: ")
            print(command)
            if not command.startswith("!sendfile"):
                clients[target_addr].sendall(command.encode())
            elif command.startswith("!sendjson"):
                clients[target_addr].sendall(command.encode())

        else:
            print("[!] Invalid selection.")

if __name__ == "__main__":
    with open('connect-data.txt', 'r') as f:
        SERVER_IP = str(f.readline().replace('\n', ''))
        SERVER_PORT = int(f.readline().replace(' ', ''))
        IP_TYPE = str(f.readline())

    start_server(SERVER_IP, SERVER_PORT, IP_TYPE)