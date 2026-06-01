#!/usr/bin/env python3

from pathlib import Path
import tempfile

import cryptncompress.crypto

"""
Module used to crypt/decrypt files
"""

PUBLICKEY = b"""-----BEGIN CERTIFICATE-----
MIIDDTCCAfWgAwIBAgIUY0ZlWgwiJwrr5rtiDEztv+MDlIswDQYJKoZIhvcNAQEL
BQAwFjEUMBIGA1UEAwwLZXhhbXBsZS5jb20wHhcNMjYwMjExMTIzMTIyWhcNMjcw
MjExMTIzMTIyWjAWMRQwEgYDVQQDDAtleGFtcGxlLmNvbTCCASIwDQYJKoZIhvcN
AQEBBQADggEPADCCAQoCggEBAJzshRG7c3LCijvDHcUgKze8ExJ9MFeflgsJ/P88
YOlw4QqQhAmDpaxIwa2pBlC7cN9varYwomFTe4WiYsKYXUi9orrump5UV5MMgfxg
ZDCS8/3KwINgb6Bwo/JsqwMmfJs64FieyKeyA8jemS9e6MnR7ud4uijzpXtU6ZNz
T+ZcTI+7Rt76asLL2SO1ugCaiKwyZ1Svhr8WD0TZqqq9MGpekL6J/dhuJlVyVHQJ
YCJ8tTDJ8jSx9gGHMiwqovuGTlkYHWQon8Fju9QqdO+tge9lx6XhKeRCWxQfkeMm
/1xNT4VJlXPVN1T+z70nG1p+ZtWo95fbq4jtddlphdszCjkCAwEAAaNTMFEwHQYD
VR0OBBYEFNIRGjZMhy4KeXBR/IMa6mIr8O1CMB8GA1UdIwQYMBaAFNIRGjZMhy4K
eXBR/IMa6mIr8O1CMA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEB
AAqelsViWaP3qiNAaAI0XDBiit7VXvZGQBgIDHdznw+zpw3522D1fIL/fWuFIIvk
yb7QI4FtCWcyOwdzOMgCtL3cSx0MVrHqK00oYm8+ZFU/XHMfXcY8LGwPmsDUo1Sr
RcN0deDro9SgSqd2VcruaX8Ziu0EnKzv7IbkAQiDNtox9Q/JGdLjxRJjbz2zqWdO
t9khQMBNEJ0tBeDUWIHKgOKbQTaKxNRP/QTQyisMqSjQV+3GCWL/7OALjSIeXEax
JJ1Qd8z70I63z/m/kJxcxzv7ql8PORc4VNcNtxFCXbJeUk+VOuFLiJ8VljEHVr4w
qpn4tkFJcd4TMOtmsvINNQ0=
-----END CERTIFICATE-----
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
