import argparse

from const import BOT_NAME, HEADERS_AUTH, HEADERS

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

    args = parser_root.parse_args()
    try :
        args.func(args)
    except AttributeError :
        parser_root.print_help()
