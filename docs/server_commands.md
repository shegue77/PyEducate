# Server Commands List

## Client Number


| Client Number | Description                                          |
|---------------|------------------------------------------------------|
| `0`           | Broadcasts command to all clients.                   |
| `1+`          | Sends command to selected client (from client list). |

**ℹ️ If command does not run, please try not using client numbers (if applicable).**


## General Commands

| Command    | Description                                      |
|------------|--------------------------------------------------|
| `!help`    | Opens the help list.                             |
| `!info`    | Shows server information.                        |
| `!version` | Displays the current version of the application. |
| `!license` | Shows the license information.                   |

## Client Information

| Command        | Description                                     |
|----------------|-------------------------------------------------|
| `!getip`       | Retrieves the public IPv4 address of client(s). |
| `!gethostname` | Retrieves the hostname of client(s).            |
| `!getusername` | Retrieves the username of client(s).            |

## Leaderboard & Lessons

| Command                          | Description                                                       | Example                                                              |
|----------------------------------|-------------------------------------------------------------------|----------------------------------------------------------------------|
| `!getstats`                      | Retrieves leaderboard data for client(s).                         | -                                                                    |
| `!updateboard [path]`            | Parses and sends leaderboard data of the top 10 from a JSON file. | `!updateboard leaderboards.json`                                     |
| `!sendlesson <lesson_ID> [path]` | Sends specific lesson(s) to client(s) from a JSON file.           | `!sendlesson [2] lessons.json`<br>`!sendlesson [1,3,4] lessons.json` |
| `!sendjson [path]`               | Sends a JSON file containing all lessons to client(s).            | `!sendjson lessons.json`                                             |

## Client Management

| Command                                 | Description                                                                 | Example                             |
|-----------------------------------------|-----------------------------------------------------------------------------|-------------------------------------|
| `!showblacklist`                        | Displays all banned IP addresses.                                           | -                                   |
| `!ban <IP_ADDRESS> [reason] [severity]` | Bans an IP from connecting.                                                 | `!ban 127.0.0.1 port_scanning high` |
| `!unban <IP_ADDRESS>`                   | Removes a ban from an IP.                                                   | `!unban 127.0.0.1`                  |
| `!disconnect`                           | Disconnects client(s).                                                      | -                                   |
| `!shutdown`                             | Safely disconnects all clients and shuts down the server. Use with caution. | -                                   |

## Notes

- Arguments in `< >` are **required**.  
- Arguments in `[ ]` are **optional**.
