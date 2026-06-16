# Crypt'n Compress

The library is used in the lola project to encrypt, decrypt, compress and extract dataset or files.

## Versions

You can find all versions of Crypt'n Compress on the [release page](https://gitlab.inria.fr/lola/back-end/cryptncompress/-/releases)

## Download package

### In requirements.txt
You can add this repository into your `Requirements.txt` file and specify the tag version.

```bash
$ cat requirements.txt
git+ssh://git@gitlab.inria.fr/lola/back-end/cryptncompress.git@2.0.0

$ pip install -r requirements.txt
...
Successfully installed cryptncompress-2.0.0

$ python -c "import cryptncompress"
```

### From CLI

```
API_TOKEN=mc6FUyiA6d6Dksygpg33
pip install cryptncompress --extra-index-url https://__token__:${API_TOKEN}@gitlab.inria.fr/api/v4/projects/29064/packages/pypi/simple
```

## How to use

### Crypto part

You need a couple of 2048 rsa keys with x509 before. To generate them, use openssl.

```bash
openssl req -x509 -nodes -newkey rsa:2048 -keuout private_key.pem -out public_key.pem
```

Generate a file with data inside

```bash
cat

```

```python
from pathlib import Path
from cryptncompress import crypto

PATH_PRIVATE_KEY = Path("/home/pnoel/Documents/lola/lola-private.pem")
PATH_PUBLIC_KEY = Path("/home/pnoel/Documents/lola/lola-public.pem")



```

