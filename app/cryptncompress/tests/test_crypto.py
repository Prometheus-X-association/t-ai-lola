#!/usr/bin/env python3

import pytest

from cryptncompress.crypto import FileType, DataFile, SymmetricKey
from cryptncompress import errors
from cryptncompress.crypto import fix_binary_data_length


def test_fix_binary_data_length_block14():
    # fix block of size 16. So with a block of size 14, It should
    # add 2 bytes
    my_data = b"0"*14
    assert len(my_data) == 14
    fixed_data, _ = fix_binary_data_length(my_data)
    assert len(fixed_data) == SymmetricKey.key_size


def test_fix_binary_data_length_block17():
    # fix block of size 16. So with a block of size 17, It should
    # add 15 bytes
    my_data = b"0"*17
    assert len(my_data) == 17
    fixed_data, _ = fix_binary_data_length(my_data)
    assert len(fixed_data) == 32


def test_filetype_str_to_bin():
    assert FileType.str_to_bin("file") == b"\x00"
    assert FileType.str_to_bin("xapi") == b"\x01"


def test_filetype_str_to_bin_incorrectFileType():
    # Should fail
    with pytest.raises(errors.CryptoIncorrectFileType):
        FileType.str_to_bin("toto")


def test_filetype_bin_to_str():
    assert FileType.bin_to_str(b"\x00") == "file"
    assert FileType.bin_to_str(b"\x01") == "xapi"


def test_filetype_bin_to_str_FileType_not_integer():
    # Cannot convert the 8 first bits into an integer
    # toto 2 times to avoid raising errors.FileTypeFunctionError
    with pytest.raises(errors.FileTypeFunctionError):
        FileType.bin_to_str(b"totototo")


def test_filetype_bin_to_str_unknowFileType():
    # Cannot convert the 8 first bits into an integer
    with pytest.raises(errors.FileTypeFunctionError):
        FileType.bin_to_str(b"00000010")


def test_filetype_bin_to_str_wrongByteSize():
    # Fail if binary size != 8bits
    with pytest.raises(errors.FileTypeFunctionError):
        FileType.bin_to_str(b"1"*5)
        FileType.bin_to_str(b"1"*9)


def test_datafile_int_to_bin():
    assert DataFile.int_to_bin(5, 1) == b"\x05"
    assert DataFile.int_to_bin(5, 2) == b"\x00\x05"


def test_datafile_int_to_bin_overflow():
    with pytest.raises(OverflowError):
        DataFile.int_to_bin(256, 1)


def test_datafile_bin_to_int():
    assert DataFile.bin_to_int(b"\x01"), 1
    assert DataFile.bin_to_int(b"\x00\x00\x00\x00\x00\x01\xe2@"), 123456
