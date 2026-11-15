"""Helpers to build URLs of the services used by Lolapy."""

import os


def default_scheme() -> str:
    """Scheme used when an address has none.

    Configurable with the environment variable `LOLAPY_URL_SCHEME` ("http" or "https").
    Set to `https` by default.
    """
    scheme = os.environ.get("LOLAPY_URL_SCHEME", "https").lower()
    if scheme not in ("http", "https"):
        raise ValueError(f"LOLAPY_URL_SCHEME must be 'http' or 'https'. Got '{scheme}'")
    return scheme


def with_scheme(address: str) -> str:
    """Return `address` prefixed by the default scheme if it has no scheme."""
    if "://" in address:
        return address
    return f"{default_scheme()}://{address}"
