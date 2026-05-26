#!/usr/bin/env python3

import argparse
import os
import sys
import tempfile
from pathlib import Path

from tqdm import tqdm

from src import crypto
from src import archive
from src import connection
# from src import lib

class DownloadProgressBar(tqdm):
    def update_to(self, current, total):
        self.total = total
        self.update(current - self.n)

class _HelpAction(argparse._HelpAction):
    """
    Override HelpAction class to print help for all subcommands
    """

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

class GetPath:
    """
    Manage Path for code launched with Python or with pysintaller
    """

    @staticmethod
    def get(relative_path: Path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = Path(sys._MEIPASS)
        except Exception:
            base_path = Path(".").absolute()

        return base_path / relative_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepare Data program for LOLA. Can encrypt or decrypt files for Lola platform",
        add_help=False,
    )
    # Edit the --help command to print informations on all sub-command
    parser.add_argument(
        "-h", "--help", action=_HelpAction, help="show this help message and exit"
    )

    parser.add_argument(
        "-v", "--version", action="store_true", help="Print version of the program"
    )

    create_parsers = parser.add_subparsers(help="sub-command help")

    parser_decrypt = create_parsers.add_parser(
        "decrypt", help="Decrypt and uncompress file using private key"
    )
    parser_decrypt.set_defaults(command="decrypt")
    parser_decrypt.add_argument(
        "--private-key", help="Private key used to decrypt file", required=True
    )
    parser_decrypt.add_argument(
        "--crypted-file", help="Path of the crypted file", required=True
    )
    parser_decrypt.add_argument(
        "--output",
        help="Path of the folder to store bordereau and dataset",
        required=True,
    )

    parser_encrypt = create_parsers.add_parser(
        "encrypt", help="Compress and Encrypt bordereau and dataset"
    )
    parser_encrypt.set_defaults(command="encrypt")
    parser_encrypt.add_argument(
        "--bordereau", help="Path to the Bordereau file", required=True
    )
    parser_encrypt.add_argument(
        "--dataset", help="Path to the dataset file", required=True
    )
    parser_encrypt.add_argument(
        "--output", help="Path for the output crypted file", required=True
    )
    parser_encrypt.add_argument(
        "--sftp-send",
        help="Send file to sftp server after encryption",
        action="store_true",
    )

    args = parser.parse_args()

    if args.version:
        # print(f"Lolapy version: '{lib.LOLA_TOOLBOX_VERSION}'")
        sys.exit(0)

    ## If the scipt is run without argument
    if len(sys.argv) == 1:
        # Load GUI here to avoid loading PySimpleGUI on servers or no GUI environment
        from src import GUI

        my_gui = GUI.Window()
        my_gui.start()
        sys.exit(0)

    ## Part for CLI commands
    if args.command == "encrypt":
        dataset = Path(args.dataset)
        bordereau = Path(args.bordereau)
        output_file = Path(args.output)
        sftp_send: bool = args.sftp_send

        _, tmp_zippath = tempfile.mkstemp()
        tmp_zippath = Path(tmp_zippath)

        try:
            archive.compress([bordereau, dataset], tmp_zippath)

            crypto.encrypt_file(tmp_zippath, output_file, "xapi")
        finally:
            os.remove(tmp_zippath)

        if sftp_send:
            my_sftp = connection.sftp()
            my_sftp.init_connection()
            with DownloadProgressBar(unit="B", unit_scale=True) as t:
                my_sftp.put(output_file, callback=t.update_to)
            print("Transfer complete")

    if args.command == "decrypt":
        output_folder = Path(args.output)
        private_key = Path(args.private_key)
        crypted_file = Path(args.crypted_file)

        try:
            _, tmp_zippath = tempfile.mkstemp(suffix=".zip")
            tmp_zippath = Path(tmp_zippath)
            crypto.decrypt_file(crypted_file, tmp_zippath, private_key)

            archive.extract(
                input_archive=tmp_zippath, output_directory=output_folder
            )
        finally:
            os.remove(tmp_zippath)
