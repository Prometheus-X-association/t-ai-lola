#!/usr/bin/env python3

import setuptools
import os
import sys
from pathlib import Path

from sandbox import app
sandbox_version = app.__version__

MINIMAL_PYTHON_VERSION = (3, 10, 0)
LITTERAL_PYTHON_VERSION = ".".join([str(ii) for ii in MINIMAL_PYTHON_VERSION])

def check_python_version():
    """Check if the python version required is satisfied.

    Setuptools can check the python version, but only after installation of all
    packages. So if you use hints (typing) or new feature, the installation will
    break without a clear message.
    """
    if sys.version_info < MINIMAL_PYTHON_VERSION:
        current_python_version = f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"
        sys.exit(f"Python version required >= '{LITTERAL_PYTHON_VERSION}'. You have '{current_python_version}'")

def get_requirements():
    """Extract list of Python packages from requirements.txt file.

    Returns:
        list[str]: The list of Python packages
    """
    lib_folder = Path(os.path.realpath(__file__)).parent
    requirement_path = lib_folder / "requirements.txt"
    install_requires = []
    if requirement_path.is_file():
        with open(requirement_path) as f:
            install_requires = f.read().splitlines()
    else:
        print(f"'{requirement_path}' is not a file. Stop")
        sys.exit(1)
    return install_requires

if __name__ == "__main__":
    check_python_version()
    setuptools.setup(
        name="lola-sandbox",
        version=sandbox_version,
        author="Philippe N.",
        author_email="philippe.noel@loria.fr",
        description="Sandbox tool to test/run scenario and algorithms on your local device",
        packages=setuptools.find_packages(include=['sandbox', 'sandbox.*']),
        install_requires=get_requirements(),
        classifiers=[
            "Programming Language :: Python :: 3",
        ],
        entry_points = {
        'console_scripts': ['lola-sandbox=sandbox.app:main'],
        },
        python_requires='>=3.10',
    )
