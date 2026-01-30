import argparse

from const import BOT_NAME, HEADERS_AUTH, HEADERS

from commands import main as main_commands
from run import main as main_run


if __name__ == "__main__" :
    parser_root = argparse.ArgumentParser(
        prog=BOT_NAME,
        description="Hermaeus (a discord bot for archiving messages) backend and management tools."
    )
    subparsers_root = parser_root.add_subparsers()

    parser_run = subparsers_root.add_parser("run", help="Start Hermaeus backend.")
    parser_run.add_argument("--quiet", "-q", help="reduce the verbosity", action="store_true")
    parser_run.set_defaults(func=main_run)

    parser_commands = subparsers_root.add_parser("commands", help="Manage Hermaeus commands.")
    parser_group_commands = parser_commands.add_mutually_exclusive_group(required=True)
    parser_group_commands.add_argument("--list", "-l",
        help="Fetch and list the commands currently on discord. (name, id)", 
        action='store_true', 
    )
    parser_group_commands.add_argument("--show", "-s",
        help="Fetch and display the commands currently on descord details. Specify command(s) name to get only them.", 
        type=str,
        nargs="*",
        dest="command.name"
    )
    parser_group_commands.add_argument("--update", "-u",
        help="Resend all commands from the commands directory. Commands with the same names will be overwriten.", 
        action='store_true', 
    )
    parser_group_commands.add_argument("--delete", "-d",
        help="Delete the specified command(s). Must be valid command id(s), use --list.",
        type=str,
        nargs="+",
        dest="command.id"
    )
    parser_commands.set_defaults(func=main_commands)

    args = parser_root.parse_args()
    try :
        args.func(args)
    except AttributeError :
        parser_root.print_help()
