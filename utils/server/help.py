# Displays help data for commands.
def help_data():
    data = """

Available Commands:

    !help
        Opens the help list.

    !info
        Shows information of the server.

    !version
        Shows the version of the application.

    !license
        Shows the license of the application.

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
        Example: !updateboard leaderboards.json

    !sendlesson <lesson_ID> [path]
        Sends specific lesson(s) from a JSON file containing lessons (identified by ID) to client(s).
        Example 1: !sendlesson [2] lessons.json
        Example 2: !sendlesson [1, 3, 4] lessons.json

    !sendjson [path]
        Sends a JSON file containing ALL lessons to client(s).
        Example: !sendjson lessons.json

    !showblacklist
        Displays the list of all banned IP addresses.

    !ban <IP_ADDRESS> [reason] [severity]
        Bans (prevents) an IP address from connecting to the server.
        Example: !ban 127.0.0.1 port_scanning high

    !unban <IP_ADDRESS>
        Removes the ban from the specified IP address.
        Example: !unban 127.0.0.1

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


def show_license():
    data = """
PyEducate Server - Server application used to send data such as lessons to clients.
Copyright (C) 2025 shegue77

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
    return data


def show_version(app_version):
    data = f"""
PyEducate Server {app_version} | Copyright (C) 2025 shegue77
This program comes with ABSOLUTELY NO WARRANTY.
This software is released under the GNU GPL; run !license for details.
"""
    return data
