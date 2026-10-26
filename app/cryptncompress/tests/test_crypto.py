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


# ---- Encrypt / Decrypt round trip (AES-256-GCM) ----

import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptncompress import crypto
from cryptncompress.crypto import Encrypt, Decrypt


@pytest.fixture(scope="module")
def keypair(tmp_path_factory):
    d = tmp_path_factory.mktemp("keys")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(name).public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now).not_valid_after(now + datetime.timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    pub = d / "public.pem"
    priv = d / "private.pem"
    pub.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    priv.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ))
    return pub, priv


@pytest.mark.parametrize("size", [0, 1, 31, 32, 33, 1000, 3 * 64 + 5, 3 * 64])
def test_roundtrip(tmp_path, keypair, monkeypatch, size):
    monkeypatch.setattr(crypto, "CHUNK_SIZE", 64)  # force multi chunk files
    pub, priv = keypair
    data = bytes(range(256)) * (size // 256 + 1)
    data = data[:size]
    src = tmp_path / "in"; src.write_bytes(data)
    enc = tmp_path / "enc"; out = tmp_path / "out"
    Encrypt(pub).encrypt_file("file", src, enc)
    assert Decrypt(priv).decrypt_file(enc, out) == "file"
    assert out.read_bytes() == data


def test_tampered_chunk_is_rejected(tmp_path, keypair, monkeypatch):
    monkeypatch.setattr(crypto, "CHUNK_SIZE", 64)
    pub, priv = keypair
    src = tmp_path / "in"; src.write_bytes(b"A" * 200)
    enc = tmp_path / "enc"
    Encrypt(pub).encrypt_file("file", src, enc)
    raw = bytearray(enc.read_bytes()); raw[-1] ^= 1; enc.write_bytes(bytes(raw))
    with pytest.raises(errors.DecryptChunkError):
        Decrypt(priv).decrypt_file(enc, tmp_path / "out")


def test_truncated_file_is_rejected(tmp_path, keypair, monkeypatch):
    monkeypatch.setattr(crypto, "CHUNK_SIZE", 64)
    pub, priv = keypair
    src = tmp_path / "in"; src.write_bytes(b"A" * 200)
    enc = tmp_path / "enc"
    Encrypt(pub).encrypt_file("file", src, enc)
    full = enc.read_bytes()
    enc.write_bytes(full[: -(64 + SymmetricKey.tag_size)])  # drop last chunk
    with pytest.raises(errors.DecryptChunkError):
        Decrypt(priv).decrypt_file(enc, tmp_path / "out")
