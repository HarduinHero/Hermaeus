import argparse

from const import BOT_NAME

from interactive_backend import main as main_run
from harvest import main as main_harvest
from enrich import main as main_enrich, ATTACHEMENT_TYPES, EMBED_TYPES
from enum import Enum
from typing import Callable

class COMMANDS(Enum) :

    cmd: str
    func: Callable[..., object]

    RUN = ("run", main_run)
    HARVEST = ("harvest", main_harvest)
    ENRICH = ("enrich", main_enrich)

    def __new__(cls, cmd, func):
        obj = object.__new__(cls)
        obj._value_ = cmd
        obj.cmd = cmd
        obj.func = func
        return obj

def main() :

    parser_root = argparse.ArgumentParser(
        prog=BOT_NAME,
        description="Hermaeus (a discord bot for archiving messages) backend and management tools."
    )
    subparsers_root = parser_root.add_subparsers()

    parser_run = subparsers_root.add_parser(COMMANDS.RUN.cmd, help="Start Hermaeus interactive backend.")
    parser_run.set_defaults(cmd=COMMANDS.RUN, func=COMMANDS.RUN.func)

    parser_harvest = subparsers_root.add_parser(COMMANDS.HARVEST.cmd, help="Harvest a given guild according to its state file.")
    parser_harvest_meg = parser_harvest.add_mutually_exclusive_group(required=True)
    parser_harvest_meg.add_argument("--list-harvestables", "-l", help="List the harvestables guilds.", action="store_true")
    parser_harvest_meg.add_argument("--guild-id", "-g", help="The guild that must be harvested.", type=int, dest="GUILD_ID")
    parser_harvest.set_defaults(cmd=COMMANDS.HARVEST, func=COMMANDS.HARVEST.func)

    parser_enrich = subparsers_root.add_parser(COMMANDS.ENRICH.cmd, help="Enrich a harvest by requesting the specified content.")
    parser_enrich_meg = parser_enrich.add_mutually_exclusive_group(required=True)
    parser_enrich_meg.add_argument("--list-enrichables", "-l", help="List the enrichables harvests. Harvests older than 24h cant be enriched.", action="store_true")
    parser_enrich_meg.add_argument("--target", "-t", help="Specify the target/harvest INDEX in the listed enrichables (--list-enrichables)", type=int, dest="TARGET_INDEX")
    parser_enrich_attachements_meg = parser_enrich.add_mutually_exclusive_group()
    parser_enrich_attachements_meg.add_argument("--attachement", "-a", help="Collect attachements of designated type(s).", type=ATTACHEMENT_TYPES, choices=ATTACHEMENT_TYPES, nargs="+", dest="ATTACHEMENT_TYPES")
    parser_enrich_attachements_meg.add_argument("--all-attachement", "-A", help="Collect all attachements of every type(s).", action="store_true")
    parser_enrich_embeds_meg = parser_enrich.add_mutually_exclusive_group()
    parser_enrich_embeds_meg.add_argument("--embeds", "-e", help="Collect embeds of designated type(s).", type=EMBED_TYPES, choices=EMBED_TYPES, nargs="+", dest="EMBED_TYPES")
    parser_enrich_embeds_meg.add_argument("--all-embeds", "-E", help="Collect all embeds of every type(s).", action="store_true")
    parser_enrich.set_defaults(cmd=COMMANDS.ENRICH, func=COMMANDS.ENRICH.func)



    args = parser_root.parse_args()

    print(args)


    if len(vars(args)) == 0 :
        parser_root.print_help()
        return exit()
    
    elif args.cmd == COMMANDS.ENRICH :
        if  args.TARGET_INDEX is not None and \
            args.ATTACHEMENT_TYPES is None and \
            args.EMBED_TYPES is None and \
            not(args.all_attachement) and \
            not(args.all_embeds) :
            raise parser_root.error("When usin --target/-t you must specify attachements and/or embeds to collect.")

    args.func(args)


if __name__ == "__main__" :
    main()