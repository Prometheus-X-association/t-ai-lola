#!/usr/bin/env python3

"""
``crypto`` module
=================

Module used to encrypt/decrypt files in the lola project in a specific format (see below)

:Example:
from pathlib import Path
regular_file = pathlib.Path("/tmp/my_file.txt")
with open("<PATH_TO_PUB_KEY>", "rb") as buffer_pub_key:
   pub_key_bytes = buffer_pub_key.read()

encryptor = Encrypt(pub_key_bytes)
encryptor.encrypt_file("file", regular_file, "/tmp/my_file.txt.crypt")

encrypted_file = pathlib.Path("/tmp/my_file.txt.crypt")

with open("<PATH_TO_PRIVATE_KEY>", "rb") as buffer_private_key:
    private_key_bytes = buffer_private_key.read()

decryptor = Decrypt(private_key_bytes)
decryptor.decrypt_file(encrypted_file, "/tmp/my_file.txt.descrypted")


Encryption
----------
To encrypt files, you need to have 3 items and 1 optionnal:
- The dataset file: in json, xapi or whatever. It contains data you want to
transfert on the plateform
- The format of dataset file: If the file is xapi/json or not. This is used to
make a difference between dataset files to import in platforme and "file to transfert"
- A RSA public key (2048 bits) with x509.
- (Optionnal) A bordereau file: used if the dataset file is Json/xapi and need to be import in the platform

Decryption
----------
To decrypt a file, you need 2 items:
- An encrypted file
- A RSA private key (2048 bits)

File format
-----------
The format used for encryption and decryption is specific to Lola project.
It's a binary files with the following format:
- [1 Byte INTEGER]: type of the file:
  - 1 means the file contains a xapi/json dataset, a bordereau and can be transfert to the lola platform
  - 0 means the file is just a datafile to tranfert and can be converted with other tools later.
- [256 Bytes] AES symmetric key used to fast encryption/decryption of data blob. The AES key is encrypted with the RSA key
- [8 bytes INTEGER]: Size of the dataset in bytes into a 64bits integer
- [Remains] data blob. This blob could be compressed

RSA keys
--------
Couple of RSA keys can be generated with openssl with the following command
$ openssl req -x509 -nodes -newkey rsa:2048 -keuout private_key.pem -out public_key.pem
"""

import os
from pathlib import Path

from cryptncompress import errors

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


CHUNK_SIZE = 2**25  # Easy to fit in memory


def fix_binary_data_length(binary_data: bytes):
    """
    Right padding of binary data with 0 bytes
    Fix "ValueError: The length of the provided data is not a multiple of the block length."
    """
    block_length = SymmetricKey.key_size
    binary_data_length = len(binary_data)
    length_with_padding = (
        binary_data_length + (block_length - binary_data_length) % block_length
    )
    return binary_data.ljust(length_with_padding, b"\0"), binary_data_length


def sanitize_binary_data(binary_data: bytes, original_file_size: int = None) -> bytes:
    """
    Remove all '0' added at the end of the file by the fix_binary_data_length function
    If original file_size is given, guess the number of '0' added.
    You should use original_file_size every time to avoid break the output file. For exemple
    zip files add 4 '0' at the end of the file.

    :param binary_data: data to sanitize
    :type binary_data: bytes
    :param original_file_size: size in bytes of the original file [Default: None]
    :type original_file_size: int
    :return: binary data after removing trailing '0'
    :rtype: bytes
    """
    if original_file_size:
        # Use the same calculation than in fix_binary_data_length
        length_with_padding = (
            original_file_size + (SymmetricKey.key_size - original_file_size) % SymmetricKey.key_size
        )
        number_added_0 = length_with_padding - original_file_size
        return binary_data[: len(binary_data) - number_added_0]

    while binary_data[-1] == 0:
        binary_data = binary_data[:-1]
    return binary_data


class FileType:
    """
    Class used to convert the type of file in binary format
    Don't use this class directly. This class is used by Encrypt and Decrypt class.
    2 types of files availables:
      - 'xapi' for files with xapi/json format which need to be insert directly to the platform.
      - 'file' for files that just need to be transfered. These file are not directly manage by the platform

    NOTE:   In Python 3.10. Enums and pattern matching are available and can be used instead of string representation.
            Instead of using encryptor.encrypt_file("file", input_file, output_file)
            use this instead encryptor.encrypt_file(FileType.FILE, input_file, output_file)
    TODO:   Change the note above in python 3.10
    """

    supported_types = {
        "xapi": 1,
        "file": 0,
    }
    int_size = 1 # Encode filetype on only 1 byte

    @staticmethod
    def __list_supported_types_str() -> list:
        """
        Return the supported types as a list of str
        """
        return list(FileType.supported_types)

    @staticmethod
    def str_to_bin(file_type: str) -> bytes:
        """
        Convert the string representation of a filetype ("xapi" or "file") into
        its binary representation

        :param file_type: String representation of the file type
        :type file_type: str
        :return: Binary representation of the file type
        :rtype: bytes
        """
        supported_list = FileType.__list_supported_types_str()
        if file_type not in supported_list:
            raise errors.CryptoIncorrectFileType(
                f"Unsupported File Type. Supported types : {' ,'.join(supported_list)}. Given '{file_type}'"
            )
        # Convert the integer of the file type to a binary with padding on 1 Byte
        int_file_type = FileType.supported_types[file_type]
        binary_integer = DataFile.int_to_bin(int_file_type, 1)
        return binary_integer

    @staticmethod
    def bin_to_str(bin_str: bytes) -> str:
        """
        Convert the binary representation of a filetype (0 or 1) into
        its string representation

        :param bin_str: Binary representation of the file type
        :type file_type: bytes
        :return: String representation of the file type
        :rtype: string
        """
        if len(bin_str) != FileType.int_size:
            raise errors.FileTypeFunctionError(
                f"Method bin_to_str() take a {FileType.int_size} byte as input. {len(bin_str)} bytes given."
            )
        try:
            integer_file_type = DataFile.bin_to_int(bin_str) # Convert the binary to integer
        except ValueError:
            raise errors.CryptoIncorrectFileType(
                "8 first bits of the file are not an Integer. Cannot convert the 8bits to an integer."
            )
        for (key, val) in FileType.supported_types.items():
            if val == integer_file_type:
                return key
        # Outside the loop means the value cannot be found. So raise an error
        raise errors.CryptoIncorrectFileType(
            f"Unknow integer. Cannot convert the integer to a known FileType. Given '{integer_file_type}'"
        )


class DataFile:
    """
    Class to compute information on the data file to compress (size)
    """
    @staticmethod
    def size_file_to_bin(input_file: Path) -> bytes:
        """
        Compute size and return the value into a 8 Bytes binary representation
        :param input_file: Path to the file to analyze
        :type input_file: Path
        :return: Size of the file as 8 Bytes bytes
        :rtype: bytes
        """
        file_size = input_file.stat().st_size
        return DataFile.int_to_bin(file_size, 8)

    @staticmethod
    def int_to_bin(integer: int, length: int = 1) -> bytes:
        """
        Convert an integer to a binary representation with Big endian

        :param integer: Int to convert to binary
        :type integer: int
        :param length: The length of the binary representation. 1 mean the integer
        will be on 8bits (max 255)
        :type length: int
        :return: Binary representation of the integer
        :rtype: bytes
        """
        return (integer).to_bytes(length, "big")

    @staticmethod
    def bin_to_int(binary: bytes) -> int:
        """
        Convert a byte into integer

        :param binary: The byte(s) to convert
        :type binary: bytes
        :return: A integer
        :rtype: int
        """
        return int.from_bytes(binary, "big")


class SymmetricKey:

    key_size = 32  # in bytes
    iv_size = 16  # in bytes

    def __init__(self, key: bytes, iv: bytes = None):
        """
        Create a SymmetricKey object.
        **Note**: You should use the method gen_key() instead of this constructor

        :param key: Binary Key. The size have to match SymmetricKey.key_size
        :type key: bytes
        :param iv: Binary key to use as IV (mode). The size have to match SymmetricKey.iv_size
        :return: SymmetricKey structure
        :rtype: SymmetricKey
        """
        self.key = key
        self.iv = iv
        self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv))

    @staticmethod
    def from_binary_data(
        encrypted_keys: bytes, private_key: "AsymmetricPrivateKey"
    ) -> "SymmetricKey":
        """
        Decrypt symetric keys (key + iv) from binary data.
        """
        if len(encrypted_keys) != AsymmetricPublicKey.key_size:
            raise errors.DecryptSymmetricKeyError(
                f"Wrong binary size. Should be {AsymmetricPublicKey.key_size}bytes large. You gave {len(encrypted_keys)}bytes"
            )
        decrypted_keys = private_key.decrypt(encrypted_keys)
        key = decrypted_keys[0:SymmetricKey.key_size]
        iv = decrypted_keys[SymmetricKey.key_size:]
        return SymmetricKey(key=key, iv=iv)

    @staticmethod
    def gen_aes_key() -> "SymmetricKey":
        """
        Generate a Cipher AES

        :return: A  structure
        :rtype: cryptography.hazmat.primitives.ciphers.Cipher
        """
        aes_key = os.urandom(SymmetricKey.key_size)
        iv_key = os.urandom(SymmetricKey.iv_size)
        return SymmetricKey(key=aes_key, iv=iv_key)

    def encrypt(self, binary_txt: bytes) -> bytes:
        encryptor = self.cipher.encryptor()
        data, _ = fix_binary_data_length(binary_txt)
        cipher_text = encryptor.update(data) + encryptor.finalize()
        return cipher_text

    def decrypt(self, binary_txt: bytes) -> bytes:
        decryptor = self.cipher.decryptor()
        data = decryptor.update(binary_txt)
        return data


class AsymmetricPublicKey:
    """
    RSA public key
    """

    key_size = 256
    padding = padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )
    padding_size = 256

    def __init__(self, public_key: RSAPublicKey):

        if public_key.key_size / 8 != AsymmetricPublicKey.key_size:
            # public_key.key_size is in bits and AsymmetricPublicKey.key_size in bytes
            raise errors.AsymmetricKeyError(
                f"RSA public key should have a size of 256 bits. Got {public_key.key_size}"
            )
        self.public_key = public_key

    @staticmethod
    def load_from_file(path_pub_key: Path) -> "AsymmetricPublicKey":
        with open(path_pub_key, "rb") as buffer_pub_key:
            pub_key = buffer_pub_key.read()
            x509_key = x509.load_pem_x509_certificate(pub_key)
            return AsymmetricPublicKey(x509_key.public_key())

    def encrypt_symmetric_keys(self, symmetric_key: "SymmetricKey"):
        data = symmetric_key.key + symmetric_key.iv
        return self.encrypt(data)

    def encrypt(self, binary_txt: bytes):
        """
        Encrypt a bytes with the public key
        """

        encrypted_txt = self.public_key.encrypt(
            binary_txt,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return encrypted_txt


class AsymmetricPrivateKey:
    """
    RSA private key
    """

    key_size = 256  # in bits

    def __init__(self, private_key: RSAPrivateKey):
        if private_key.key_size / 8 != AsymmetricPrivateKey.key_size:
            # private_key.key_size is in bits and AsymmetricPrivateKey.key_size in bytes
            raise errors.AsymmetricKeyError(
                f"RSA private key should have a size of {AsymmetricPrivateKey.key_size} bytes. Got {private_key.key_size}"
            )
        self.private_key = private_key

    def load_from_file(path_priv_key: Path) -> "AsymmetricPrivateKey":
        with open(path_priv_key, "rb") as buffer_priv_key:
            private_key = buffer_priv_key.read()
        private_key = serialization.load_pem_private_key(private_key, password=None)
        return AsymmetricPrivateKey(private_key)

    def decrypt(self, binary_txt: bytes):
        """
        Encrypt a bytes with the private key
        """

        decrypted_txt = self.private_key.decrypt(
            binary_txt,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return decrypted_txt


class Encrypt:
    """
    Class used to ecrypt files according to format given in the
    documentation's module
    """

    def __init__(self, path_public_key: Path):
        self.path_public_key = path_public_key

    def encrypt_file(self, file_type: str, input_file: Path, output_file: Path):
        """
        Method used to encrypt large file. The method is the same than encrypt_file but
        it streams the input_file in chunk instead of whole file in memory.

        :param file_type: type of the file. See documentation of FileType object for more information
        :type file_type: str
        :param input_file: Path to the file to encrypt
        :type input_file: pathlib.Path
        :param output_file: Path to the final encrypted file
        :type output_file: pathlib.Path
        """
        try:
            buffer_output_file = open(output_file, "wb")

            # convert file type into binary representation
            binary_filetype = FileType.str_to_bin(file_type)
            # Compute size of the file and get size into binary
            binary_file_size: bytes = DataFile.size_file_to_bin(input_file)
            # Generate symmetric key
            symmetric_key = SymmetricKey.gen_aes_key()
            # Load public key to encrypt symmetric key
            public_key = AsymmetricPublicKey.load_from_file(self.path_public_key)
            # Encrypt symmetric key
            encrypted_keys = public_key.encrypt_symmetric_keys(symmetric_key)
            # Write file type, symmetric key and size of the file in output file
            buffer_output_file.write(binary_filetype + encrypted_keys + binary_file_size)

            # Read input file by chunk, crypt every chunk and write them in output file
            with open(input_file, "rb") as i_file:
                while chunk := i_file.read(CHUNK_SIZE):
                    if len(chunk) != CHUNK_SIZE:
                        # Fix length of the last chunk by adding \'0
                        chunk, _ = fix_binary_data_length(chunk)
                        # Encrypt chunk and write it directly
                    encrypted_txt = symmetric_key.encrypt(chunk)
                    buffer_output_file.write(encrypted_txt)
        finally:
            buffer_output_file.close()


class Decrypt:
    """
    Class used to decrypt file
    """

    def __init__(self, path_private_key: Path):
        self.path_private_key = path_private_key

    def decrypt_file(self, input_file: Path, output_file: Path) -> str:
        """
        Method used to decrypt large file. The method is the same than decrypt_file but
        it streams the input_file in chunk instead of whole file in memory.

        :param input_file: Path to the file to encrypt
        :type input_file: pathlib.Path
        :param output_file: Path to the final encrypted file
        :type output_file: pathlib.Path
        :return: The string representation of the FileType ("file" or "xapi")
        :rtype: str
        """
        try:
            buffer_output_file = open(output_file, "wb")
            buffer_input_file = open(input_file, "rb")
            # Load Asymmetric private key
            private_key = AsymmetricPrivateKey.load_from_file(self.path_private_key)
            # Read 8 first bytes for the FileType
            file_type = buffer_input_file.read(FileType.int_size)
            file_type = FileType.bin_to_str(file_type)
            # Decrypt Symmetric key
            encrypted_symmetric_keys = buffer_input_file.read(AsymmetricPublicKey.key_size)
            symmetric_key = SymmetricKey.from_binary_data(encrypted_symmetric_keys, private_key)
            # Decrypt the size of the file
            binary_file_size = buffer_input_file.read(8)
            file_size = DataFile.bin_to_int(binary_file_size)

            # Read input file by chunk, crypt every chunk and write them in output file
            while chunk := buffer_input_file.read(CHUNK_SIZE):
                # Save chunk size here. After decryption, chunk variable is empty
                chunk_size = len(chunk)
                # Decrypt chunk
                decrypted_txt = symmetric_key.decrypt(chunk)
                if chunk_size != CHUNK_SIZE:
                    # remove trailing \'0 in the last chunk
                    decrypted_txt = sanitize_binary_data(decrypted_txt, file_size)
                    # Write chunk in file
                buffer_output_file.write(decrypted_txt)

            return file_type
        finally:
            buffer_input_file.close()
            buffer_output_file.close()
