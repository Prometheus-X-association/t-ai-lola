def object_fullname(o: object) -> str:
    """Return the fullname of an object with module.

    Examples:
        >>> object_fullname(socket.gaierror.__name__)
        gaierror
        >>> object_fullname(socket.gaierror)
        socket.gaierror

    Args:
        o: The object to get the full path
    Returns:
        Fullpath of the object
    """
    klass = o.__class__
    module = klass.__module__
    return module + "." + klass.__qualname__
