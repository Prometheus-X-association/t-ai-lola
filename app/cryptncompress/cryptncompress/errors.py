#!/usr/bin/env python3

class CryptErrors(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return str(self.message)


class CryptoIncorrectFileType(CryptErrors):
    """
    Error when parsing or converting the file type
    """
    pass


class FileTypeToBinError(CryptErrors):
    """
    Error when converting the integer associated to the FileType to binary 8bits
    For exemple, if you want to convert 256 to bin => 100000000 so length is 9 and not 8
    """
    pass


class FileTypeFunctionError(CryptErrors):
    """
    Error when using function/methods for FileType in the wrong way
    """
    pass


class DecryptSymmetricKeyError(CryptErrors):
    """
    Error raised when decrypt Symmetric keys
    """
    pass


class AsymmetricKeyError(CryptErrors):
    """
    Error on RSA Public Key
    """
