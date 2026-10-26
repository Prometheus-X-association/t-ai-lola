#!/usr/bin/env python3

"""
PDC (Personal Data Connector) client module.
Implements data exchange and download protocol according to VisionsTrust / PDC specification,
following the logic of the data-import project.
"""

import base64
import binascii
import gzip
import json
import logging
from pathlib import Path
import shutil
from urllib.parse import quote

import requests
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from lolapy.tools import settings


def encode_uri(s: str | bytes | None) -> str:
    """Encode `s` like the `@uri` filter of jq (RFC 3986 percent-encoding)."""
    if s is None:
        return ""
    if isinstance(s, bytes):
        try:
            s = s.decode("utf-8")
        except UnicodeDecodeError:
            return "".join(f"%{b:02X}" for b in s)
    if not isinstance(s, str):
        s = str(s)
    return quote(s, safe="-._~")


def b64_flexible_decode(s: str | bytes | None, prefer_urlsafe: bool = False) -> bytes | None:
    """Decode base64/base64url with flexible padding."""
    if s is None:
        return None
    if isinstance(s, str):
        s_bytes = s.encode("utf-8")
    else:
        s_bytes = s
    try:
        ss = s_bytes.decode("utf-8")
        padding_len = (-len(ss)) % 4
        if padding_len:
            ss += "=" * padding_len
        if prefer_urlsafe:
            return base64.urlsafe_b64decode(ss)
        return base64.b64decode(ss)
    except (binascii.Error, ValueError, UnicodeDecodeError):
        try:
            if prefer_urlsafe:
                return base64.b64decode(s_bytes)
            return base64.urlsafe_b64decode(s_bytes)
        except (binascii.Error, ValueError):
            return None


def decode_jwt_payload(token_str: str) -> dict | None:
    """Extract and parse payload from a JWT token."""
    if not token_str:
        return None
    parts = token_str.strip().split(".")
    if len(parts) < 2:
        return None
    payload_bytes = b64_flexible_decode(parts[1], prefer_urlsafe=True)
    if not payload_bytes:
        return None
    try:
        return json.loads(payload_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logging.warning(f"Could not decode JWT payload as JSON: {e}")
        return None


class PdcImporter:
    """
    Handles authentication, signature generation, contract exchange with PDC,
    retrieval of data JWT from receiver, and dataset download.
    """

    def __init__(
        self,
        contract: str,
        resource: str,
        purpose_id: str | None = None,
        resource_id: str | None = None,
    ):
        app_settings = settings.get()
        self.pdc_host = app_settings.pdc_host.rstrip("/")
        self.service_key = app_settings.pdc_service_key
        self.secret_key = app_settings.pdc_secret_key
        self.contract = contract
        self.purpose_id = purpose_id or app_settings.pdc_purpose_id
        self.resource_id = resource_id or app_settings.pdc_resource_id
        self.resource = resource

        self.pubkey_file = self._resolve_key_path(app_settings.pdc_pubkey_file, default_name="pubkey.pem")
        self.privkey_file = self._resolve_key_path(app_settings.pdc_privkey_file, default_name="privkey.pem")

        self.receiver_host = app_settings.pdc_receiver_host.rstrip("/")
        self.receiver_service = app_settings.pdc_receiver_service_key
        self.receiver_secret = app_settings.pdc_receiver_secret_key

        self.pdc_token = None
        self.receiver_token = None
        self.data_jwt = None

    def _resolve_key_path(self, key_path: Path | str, default_name: str) -> Path:
        """Resolve key file location checking multiple plausible directories."""
        path = Path(key_path)
        if path.is_absolute() and path.exists():
            return path

        candidates = [
            path,
            Path.cwd() / path,
            Path(__file__).resolve().parent.parent / path,
            Path("/app") / path,
            Path("/tmp/certs") / path.name,
            Path("/tmp/certs") / default_name,
            Path.cwd() / "certs" / default_name,
            Path(__file__).resolve().parent.parent / "certs" / default_name,
            Path.cwd() / "keys" / default_name,
            Path(__file__).resolve().parent.parent / "keys" / default_name,
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate
        return path

    def _get_pubkey_content(self) -> str:
        """Read public key PEM and normalize newlines."""
        if not self.pubkey_file.exists():
            raise FileNotFoundError(f"Public key file not found: {self.pubkey_file}")
        with open(self.pubkey_file, "r", encoding="utf-8") as f:
            data = f.read()
        return data.replace("\r\n", "\n").replace("\r", "\n")

    def _create_signature(self) -> str:
        """
        Create RSA PKCS#1 v1.5 + SHA-256 signature for:
        resource=<encoded_resource>&pubkey=<encoded_pubkey>
        """
        pubkey_data = self._get_pubkey_content()
        if not pubkey_data.endswith("\n"):
            pubkey_data += "\n"

        resource_enc = encode_uri(self.resource)
        pubkey_enc = encode_uri(pubkey_data)
        message = f"resource={resource_enc}&pubkey={pubkey_enc}".encode("utf-8")

        if not self.privkey_file.exists():
            raise FileNotFoundError(f"Private key file not found: {self.privkey_file}")

        with open(self.privkey_file, "rb") as f:
            pem_data = f.read()

        private_key = serialization.load_pem_private_key(pem_data, password=None)
        signature = private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("ascii").replace("\n", "")

    def login_pdc(self) -> str:
        """Authenticate against PDC and extract JWT token."""
        url = f"{self.pdc_host}/login"
        headers = {"Content-Type": "application/json"}
        data = {"secretKey": self.secret_key, "serviceKey": self.service_key}
        logging.info(f"Connecting to PDC login: {url}")
        resp = requests.post(url, json=data, headers=headers, timeout=20)
        if resp.status_code != 200:
            raise RuntimeError(f"PDC login failed: HTTP {resp.status_code} - {resp.text}")
        content = resp.json().get("content", {})
        self.pdc_token = content.get("token")
        if not self.pdc_token:
            raise ValueError(f"No token found in PDC login response: {resp.text}")
        return self.pdc_token

    def process_exchange(self) -> dict:
        """Execute consumer exchange request to PDC."""
        if not self.pdc_token:
            self.login_pdc()

        url = f"{self.pdc_host}/consumer/exchange"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.pdc_token}",
        }
        pubkey_str = self._get_pubkey_content()
        signature_b64 = self._create_signature()

        data = {
            "contract": self.contract,
            "purposeId": self.purpose_id,
            "resourceId": self.resource_id,
            "providerParams": {
                "query": [
                    {"resource": self.resource},
                    {"pubkey": pubkey_str},
                    {"signature": signature_b64},
                ]
            },
        }
        logging.info(f"POST {url} with contract {self.contract}")
        resp = requests.post(url, json=data, headers=headers, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"PDC exchange failed: HTTP {resp.status_code} - {resp.text}")
        return resp.json()

    def login_receiver(self) -> str:
        """Authenticate with the receiver service."""
        url = f"{self.receiver_host}/login"
        headers = {"Content-Type": "application/json"}
        data = {
            "service_key": self.receiver_service,
            "secret_key": self.receiver_secret,
        }
        logging.info(f"Connecting to receiver login: {url}")
        resp = requests.post(url, json=data, headers=headers, timeout=20)
        if resp.status_code != 200:
            raise RuntimeError(f"Receiver login failed: HTTP {resp.status_code} - {resp.text}")
        self.receiver_token = resp.json().get("token")
        if not self.receiver_token:
            raise ValueError(f"No token in receiver login response: {resp.text}")
        return self.receiver_token

    def get_from_receiver(self) -> str:
        """Retrieve data JWT from receiver service."""
        if not self.receiver_token:
            self.login_receiver()

        url = f"{self.receiver_host}/get"
        headers = {
            "Content-Type": "plain/txt",
            "Authorization": f"Bearer {self.receiver_token}",
        }
        logging.info(f"Fetching data token from receiver: {url}")
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            raise RuntimeError(f"Receiver get failed: HTTP {resp.status_code} - {resp.text}")
        self.data_jwt = resp.text.strip()
        return self.data_jwt

    def download_data(self, target_file: Path, progress_callback=None) -> int:
        """
        Download dataset from the resolved URL in Data JWT and save to target_file.
        Returns total bytes written.
        """
        if not self.data_jwt:
            self.get_from_receiver()

        payload = decode_jwt_payload(self.data_jwt)
        if not payload or "url" not in payload:
            raise ValueError(f"Invalid Data JWT: url not found in payload: {payload}")

        download_url = payload["url"]
        logging.info(f"Downloading resource from {download_url}")

        headers = {"Authorization": f"Bearer {self.data_jwt}"}
        resp = requests.get(download_url, headers=headers, stream=True, timeout=120)
        resp.raise_for_status()

        total_length = resp.headers.get("content-length")
        total_size = int(total_length) if total_length and total_length.isdigit() else None

        target_file.parent.mkdir(parents=True, exist_ok=True)
        downloaded = 0
        last_reported = -1.0

        with open(target_file, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size and progress_callback:
                        fraction = downloaded / total_size
                        if fraction - last_reported >= 0.02 or fraction >= 1.0:
                            progress_callback(min(1.0, fraction))
                            last_reported = fraction

        if progress_callback:
            progress_callback(1.0)

        # If file is gzip-compressed (e.g. .gz), ensure decompressed file is also available if needed
        if target_file.name.endswith(".gz"):
            decompressed_path = target_file.with_suffix("")
            try:
                logging.info(f"Decompressing {target_file} to {decompressed_path}")
                with gzip.open(target_file, "rb") as gz_in:
                    with open(decompressed_path, "wb") as f_out:
                        shutil.copyfileobj(gz_in, f_out)
            except (gzip.BadGzipFile, OSError) as e:
                logging.warning(f"Could not decompress gzip file {target_file}: {e}")

        return downloaded
