import socket

with open('connect-data.txt', 'r') as f:
    SERVER_IP = f.readline().replace('\n', '')
    SERVER_PORT = int(f.readline())

print(SERVER_IP)
print(SERVER_PORT)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((SERVER_IP, SERVER_PORT))
    data = s.recv(1024).decode("utf-8")
    print(data)