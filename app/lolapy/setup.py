import setuptools
import os
import sys
from pathlib import Path

"""Installation file for Lolapy package.

Usage:
    $ pip install .

Be careful when editing this file, don't use recent python feature (match/case, hinting, ...)
to avoid raising errors before the checking of the python version.
"""

lolapy_version = "1.8.0"

MINIMAL_PYTHON_VERSION = (3, 12, 0)
LITTERAL_PYTHON_VERSION = ".".join([str(ii) for ii in MINIMAL_PYTHON_VERSION])

def check_python_version():
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
    print(install_requires)
    return install_requires

if __name__ == "__main__":
    check_python_version()
    setuptools.setup(
        name="lolapy",
        version=lolapy_version,
        author="Philippe N.",
        author_email="philippe.noel@loria.fr",
        description="Backend System of the Lola Project",
        packages=setuptools.find_packages(),
        install_requires=get_requirements(),
        classifiers=[
            "Programming Language :: Python :: 3",
        ],
        python_requires=f">={LITTERAL_PYTHON_VERSION}",
    )
