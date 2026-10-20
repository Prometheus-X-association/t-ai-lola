"""Cross-site request forgery protection for the Lolapy JSON API.

Lolapy is a machine to machine API: clients (frontend backend, toolbox) are not browsers and have
no session/cookie, so synchronizer tokens cannot be used. The protection is made of two checks,
both recommended by OWASP for JSON APIs:

* State changing requests must be sent with a JSON body (`Content-Type: application/json`).
  A browser cannot send this content type cross-site without a CORS preflight, and the API
  does not allow any cross-origin request.
* If the request carries an `Origin` header (always the case for cross-site browser requests),
  it has to match the host of the API.
"""

from urllib.parse import urlsplit

from flask import Flask, Response, request

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def install(flask_app: Flask) -> None:
    """Register the CSRF guard on a Flask application."""

    @flask_app.before_request
    def csrf_guard():
        if request.method in SAFE_METHODS:
            return None

        origin = request.headers.get("Origin")
        if origin and urlsplit(origin).netloc != request.host:
            return Response("Cross-origin request refused", status=403)

        if request.content_length and not request.is_json:
            return Response("Content-Type must be application/json", status=415)
        return None
