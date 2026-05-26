<img src="img/lola_toolbox-logos.png"  width="700" height="240">  

GUI tool to prepare dataset for lola application.

[[_TOC_]]

## How to use GUI version

**Requirements for GUI:**
- GLIB_C >= 2.27
  
  
**Note**: The GUI version only allow to compress and encrypt data. No decrypt nor decompression are available with GUI. Use the CLI version instead

1. Download binary according to your system [here](https://gitlab.inria.fr/lola/lola_toolbox/-/releases)
2. Double-click on the binary

## How to use CLI version

1. Download binary according to your system [here](https://gitlab.inria.fr/lola/lola_toolbox/-/releases
)
2. In a terminal, run the binary with --help to have help on command lines. It works on windows and linux. 
```bash
./lola_toolbox_linux-x86.run --help
usage: lola_toolbox_linux-x86.run [-h] {decrypt,encrypt} ...

Prepare Data program for LOLA. Can encrypt or decrypt files for Lola platform

positional arguments:
  {decrypt,encrypt}  sub-command help
    decrypt          Decrypt and uncompress file using private key
    encrypt          Compress and Encrypt bordereau and dataset

optional arguments:
  -h, --help         show this help message and exit
---
Command 'decrypt'
usage: lola_toolbox_linux-x86.run decrypt [-h] --private-key PRIVATE_KEY --crypted-file CRYPTED_FILE --output OUTPUT

optional arguments:
  -h, --help            show this help message and exit
  --private-key PRIVATE_KEY
                        Private key used to decrypt file
  --crypted-file CRYPTED_FILE
                        Path of the crypted file
  --output OUTPUT       Path of the folder to store bordereau and dataset

---
Command 'encrypt'
usage: lola_toolbox_linux-x86.run encrypt [-h] --bordereau BORDEREAU --dataset DATASET --output OUTPUT

optional arguments:
  -h, --help            show this help message and exit
  --bordereau BORDEREAU
                        Path to the Bordereau file
  --dataset DATASET     Path to the dataset file
  --output OUTPUT       Path for the output crypted file
```

## How to build lola_toolbox executable

**Prefer the binary version of the program instead of using sources.**  

Lola_toolbox can be build with pyinstaller. Follow instructions for your device to build a single executable as those available in [release section](https://gitlab.inria.fr/lola/lola_toolbox/-/releases)

### Build for Linux 64bits

Requirements:
- Docker >= 20.10 (may works with older version but not tested)

```bash
$ docker build . -t build_lolatoolbox_linux
$ docker run -it -u$(id -u):$(id -g) -v /tmp/dist:/tmp/dist build_lolatoolbox_linux
$ mv /tmp/dist/main /tmp/dist/lola_toolbox_linux.run
$ /tmp/dist/lola_toolbox_linux.run --help 
```

### Requirements (for developpers)

- python==3.8
- pip==20.3.3
- git 
  
You have to install all required packages with python. Use pip and requirements.txt to do it. 
**For linux:**
```bash
$ pip install -r requirements.txt
```

**For windows:**  
```powershell
$ python3.exe -m pip install -r requirements.txt
```

You can run the program by running `python -m  src.main --help`. Run `python -m  src.main` without arguments to run the GUI version.

### Publish to repository package

To upload binary to the package repository, use curl command:

```bash
$ PATH_BINARY=        # path to the binary on local to upload
$ VERSION_NUMBER=     # version number according to git. Ex: 1.0.0
$ TOKEN_USER=         # Api access token used to upload data on repository
$ TOKEN_PASSWORD=     # Api access token used to upload data on repository
$ REMOTE_PATH=        # Name of the Binary on the remote. For exemple for windows binary: lola-toolbox_1.0.0_win10.exe

$ curl curl --upload-file ${PATH_BINARY} \
       "https://${TOKEN_USER}:${TOKEN_TOKEN}@gitlab.inria.fr/api/v4/projects/27921/packages/generic/lola_toolbox/${VERSION_NUMBER}/${REMOTE_PATH}"
```
