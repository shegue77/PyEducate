import socket
from os.path import join, exists
from utils.crypto import decrypt_file
from utils.server.logger import log_error
from utils.server.paths import get_appdata_path


def get_local_ip_address(ip_type):
    server_ip = ""
    if ip_type.strip() == "ipv6":
        hostname = socket.gethostname()
        try:
            for info in socket.getaddrinfo(hostname, None):
                if info[0] == socket.AF_INET6:  # Check for IPv6
                    server_ip = str(info[4][0])

            if server_ip == "":
                server_ip = input("Enter local IP address (IPv6): ")

        except socket.gaierror:
            print("Hostname could not be resolved.")
            server_ip = input("Enter local IP address (IPv6): ")

    else:
        server_ip = socket.gethostbyname(socket.gethostname())

    return server_ip


def validate_ip(ip_address):
    ip_address = ip_address.strip().split(".")
    valid_ip: bool = False

    if len(ip_address) == 4:
        for part in ip_address:
            try:
                if 0 <= int(part) <= 255:
                    valid_ip = True
                else:
                    valid_ip = False
                    break

            except ValueError:
                valid_ip = False
                break

    if ip_address[0] == "localhost":
        valid_ip = True

    return valid_ip


def get_server_data():
    full_path = get_appdata_path()
    if exists(join(full_path, "connect-data.txt")):
        with open(join(full_path, "connect-data.txt"), "rb") as f:
            data = decrypt_file(f.read()).strip().splitlines()
            server_port = data[0]
            ip_type = data[1]
            try:
                server_ip = data[2]
            except IndexError as ie:
                log_error(ie)
                server_ip = get_local_ip_address(ip_type)
    else:
        log_error(
            "FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\makin\\AppData\\Roaming\\PyEducate\\server\\connect-data.txt'"
        )
        return

    return server_ip, server_port, ip_type
