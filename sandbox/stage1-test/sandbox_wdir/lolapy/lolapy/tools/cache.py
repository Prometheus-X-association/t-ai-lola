#!/usr/bin/env python3

"""Use a separate module to allow sharing cache system to the whole library.

Do this before importing all routes to avoid missing configuration
This is used for example in /server/usage.
Use this with a decorator like the following to cache response during 50 seconds

## Example:

```python
from lolapy.tools import cache

@flask_app.route(/foo)
@cache.cache_object.cached(timeout=50)
def foo():
    print("Hello world!")
    return 1
```
If you run multiple curl on the /foo route, you will see "Hello world" printted
  in the log only every 50 secondes

PS: it does not work if cache initialisation is in the same module as flask_app (bin/app.py)
"""

from flask_caching import Cache

cache_config = {
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

cache_object = Cache(config=cache_config)
