import os
import socket
import struct
import requests
from tqdm import tqdm
from json import load, loads, dump, dumps, JSONDecodeError
from ast import literal_eval

def get_json_file(new_lesson):
    if type(new_lesson) is dict:
        try:
            dumps(new_lesson)
            print("✅ Dictionary is JSON serializable")
        except (TypeError, OverflowError, JSONDecodeError) as e:
            print("❌ Not JSON serializable:", e)
            return None

    else:
        try:
            new_lesson = loads(new_lesson)
            print("✅ JSON is valid")
        except JSONDecodeError as e:
            print("❌ Invalid JSON:", e)
            return None

    # Modify (e.g., add a lesson)
    data = new_lesson

    # Save back to file
    with open('lessons.json', 'w') as f:
        dump(data, f, indent=2)
        print('data written')

    return 'SUCCESS'



def get_mac_address():
    try:
        # Execute the getmac command to get the MAC address
        output = os.popen("getmac").read()

        # Extract the first MAC address from the output
        mac_address = output.split()[6]
        return mac_address

    except Exception as e:
        print(f"Error: {e}")
        return None

def start_client(server_ip, server_port, server_type='ipv4'):
    if server_type == 'ipv6':
        client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((server_ip, server_port))

    while True:
        print('e')
        command = client.recv(2048).decode()
        print(f"[Received Command] {command}")

        if command.lower() == "!exit":
            break

        if command.lower().split()[0] == "!sendjson":
            json_part = command[len('!sendjson '):]  # extract the JSON substring
            try:
                data = loads(json_part)
                print("Parsed JSON:", data)
            except JSONDecodeError:
                print("Invalid JSON data received")
            get_json_file(json_part)

            client.send(str(command).encode())
            continue

        if command.lower() == "!getip":
            response = requests.get('https://api64.ipify.org?format=json').json()
            client.send(response['ip'].encode())
            continue

    client.close()

if __name__ == "__main__":
    with open('connect-data.txt', 'r') as f:
        SERVER_IP = str(f.readline().replace('\n', ''))
        SERVER_PORT = int(f.readline())
        IP_TYPE = str(f.readline())

    start_client(SERVER_IP.replace('\n', ''), SERVER_PORT, IP_TYPE)