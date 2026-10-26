"""Helpers to build URLs of the services used by Lolapy."""

import os


def default_scheme() -> str:
    """Scheme used when an address has none.

    Configurable with the environment variable `LOLAPY_URL_SCHEME` ("http" or "https").
    Defaults to `http`.
    """
    scheme = os.environ.get("LOLAPY_URL_SCHEME")
    if not scheme:
        try:
            from lolapy.tools import settings
            scheme = getattr(settings.get(), "lolapy_url_scheme", None)
        except Exception:
            scheme = None
    scheme = (scheme or "http").lower()
    if scheme not in ("http", "https"):
        raise ValueError(f"LOLAPY_URL_SCHEME must be 'http' or 'https'. Got '{scheme}'")
    return scheme


def with_scheme(address: str, port: int | None = None) -> str:
    """Return `address` prefixed by the default scheme if it has no scheme."""
    if "://" in address:
        return address
    if port == 80 and os.environ.get("LOLAPY_URL_SCHEME") != "https":
        return f"http://{address}"
    return f"{default_scheme()}://{address}"
