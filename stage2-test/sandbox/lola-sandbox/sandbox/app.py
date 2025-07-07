#!/usr/bin/env python3

import argparse
import logging
import sys

__version__ = "1.0.4"

class _HelpAction(argparse._HelpAction):
    """Override HelpAction class to print help for all subcommands."""

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()

        subparsers_actions = [
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ]
        for subparsers_action in subparsers_actions:
            for choice, subparser in subparsers_action.choices.items():
                print("---\n\033[0;32mCommand '{}'\033[0m".format(choice))
                print(subparser.format_help())

        parser.exit()

def main():
    from sandbox import validate
    from sandbox import run

    parser = argparse.ArgumentParser(
        description="Manage Sandbox environment for Lola Platform",
        add_help=False,
    )
    # Edit the --help command to print informations on all sub-command
    parser.add_argument(
        "-h", "--help", action=_HelpAction, help="show this help message and exit"
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Increase verbosity")
    parser.add_argument("--version", action="version", version=__version__)

    command_choices = ("validate", "run")
    parser.add_argument(
        "command", choices=command_choices, help="Command to run", nargs=argparse.REMAINDER
    )

    # If there is no argument, print the help
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Validate that the first argument is allowed (defined in `command_choices`)
    if not args.command[0] in command_choices:
        print(f"{args.command[0]} is not a valid choices. Use '{command_choices}' instead or --help for information")
    # Set-up logging for the entire application
    logger = logging.getLogger("root")
    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s")
    if args.verbose:
        logger.setLevel("DEBUG")
        logging.debug("Verbosity set to debug")
    else:
        logger.setLevel("INFO")
    # Parse first command line argument to run the appropiate script
    match args.command[0]:
        case "validate":
            validate.parse_args_from_app(args.command[1:])
        case "run":
            run.parse_args_from_app(args.command[1:])

if __name__ == "__main__":
    main()
