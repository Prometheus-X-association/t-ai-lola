import setuptools
import os
from pathlib import Path


def get_requirements():
    """
    Extract requirements from requirements.txt file

    :return: a list of all requires
    :rtype: list<str>
    """
    lib_folder = Path(os.path.realpath(__file__)).parent
    requirement_path = lib_folder / "requirements.txt"
    install_requires = []
    if os.path.isfile(requirement_path):
        with open(requirement_path) as f:
            install_requires = f.read().splitlines()
    return install_requires


setuptools.setup(
    name="cryptncompress",
    version="2.0.0",
    author="Philippe N.",
    author_email="philippe.noel@loria.fr",
    description="Encrypt/Decrypt, compress and Decompress files in Lola project",
    packages=setuptools.find_packages(),
    install_requires=get_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.12',
)
