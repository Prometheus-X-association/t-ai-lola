#!/usr/bin/env python3

from pathlib import Path
import tempfile

import cryptncompress.crypto

"""
Module used to crypt/decrypt files
"""

PUBLICKEY = b"""
"""


def encrypt_file(input_file: Path, output_file: Path, file_type: str = "xapi"):
    """
    Encrypt a file using the cryptNcompress library
    """
    try:
        # Create temporary file to store the public key
        tmp_public_key_file = tempfile.NamedTemporaryFile()
        tmp_public_key_file.write(PUBLICKEY)
        tmp_public_key_file.flush()

        encryptor = cryptncompress.crypto.Encrypt(tmp_public_key_file.name)
        encryptor.encrypt_file(file_type=file_type, input_file=input_file, output_file=output_file)
    finally:
        tmp_public_key_file.close()


def decrypt_file(input_file: Path, output_file: Path, private_key: Path):
    """
    Decrypt a file using the cryptNcompress library
    """
    decryptor = cryptncompress.crypto.Decrypt(private_key)
    decryptor.decrypt_file(input_file=input_file, output_file=output_file)
