from argparse import Namespace
import requests
import json
from const import URL_GLOBAL_APPLICATION_COMMANDS, HEADERS_AUTH, COMMANDS_DIRECTORY
from pathlib import Path

__TIMEOUT = 10

def main(args:Namespace) -> None :
    
    args_show = args.__dict__["command.name"]
    args_delete = args.__dict__["command.id"]

    if args.list or args_show is not None:
        try :
            response = requests.get(
                url=URL_GLOBAL_APPLICATION_COMMANDS,
                headers=HEADERS_AUTH,
                timeout=__TIMEOUT
            )
        except ConnectionError :
            print("Something went wrong while fetching data.")
            return

        if response.status_code != 200 :
            print(f"Something went wrong.\n({response.status_code}) : {response.content.decode()}")
            return
        
        try:
            command_list = response.json()
        except json.JSONDecodeError:
            print("No command found.")
            return
        else :
            if args.list :
                print("Commands currently on discord :")
                print("-"*50)
                print("  - Name\t\tId")
                print("-"*50)
                for command in command_list :
                    print(f"  - {command["name"]}\t\t{command["id"]}")
            else :
                for command in command_list :
                    if len(args_show) == 0 or command["name"] in args_show :
                        print(f"- {command["name"]}:")
                        print("-"*50)
                        print(json.dumps(command, indent=2))
                        print("\n\n")

    elif args.update :
        commands_dir = Path(COMMANDS_DIRECTORY)
        if not (commands_dir.exists() and commands_dir.is_dir()) :
            raise FileNotFoundError(f"{COMMANDS_DIRECTORY}, where the commands json declaration files lives does not exist.")

        for command_file in commands_dir.iterdir() :
            with command_file.open() as command_file_fd :
                try :
                    command_data = json.load(command_file_fd)
                    response = requests.post(
                        url=URL_GLOBAL_APPLICATION_COMMANDS,
                        headers=HEADERS_AUTH,
                        json=command_data,
                        timeout=__TIMEOUT
                    )
                except json.JSONDecodeError :
                    print(f"{command_file.name} ... JSON parsing error")
                except ConnectionError :
                    print(f"{command_data["name"]} ... Something went wrong while requestion discord.")
                except TimeoutError :
                    print(f"{command_data["name"]} ... Timeout")
                else : 
                    if response.status_code == 201 :
                        print(f"{command_data["name"]} ... CREATED")
                    elif response.status_code == 200 :
                        print(f"{command_data["name"]} ... OVERWRITTEN")
                    else :
                        print(f"{command_data["name"]} ... ({response.status_code}) : {response.content.decode()}")

    elif args_delete is not None :
        for command_id in args_delete :
            try :
                response = requests.delete(
                    url=f"{URL_GLOBAL_APPLICATION_COMMANDS}/{command_id}",
                    headers=HEADERS_AUTH,
                    timeout=__TIMEOUT
                )
            except ConnectionError :
                print(f"{command_id} ... Something went wrong while requestion discord.")
            except TimeoutError :
                print(f"{command_id} ... Timeout")
            else :
                if response.status_code == 204 :
                    print(f"{command_id} ... DELETED")
                else :
                    print(f"Something went wrong.\n({response.status_code}) : {response.content.decode()}")
