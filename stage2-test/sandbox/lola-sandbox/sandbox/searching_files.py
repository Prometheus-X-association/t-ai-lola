#!/usr/bin/env python3

"""Module used to search files in directory and sub-dir"""

from pathlib import Path
import os

class SearchFiles:
    def __init__(self, files: list[Path], source: Path):
        """Constructor for SearchFiles.

        Args:
            files: list of filename to search
            source: the source directory where to search for files
        """
        self.files = files
        self.source = source

    def search(self) -> list[Path]:
        """Return a list of files matching the name"""
        file_list: list[Path] = []

        for root, _, files in os.walk(str(self.source)):
            for filename in files:
                if filename in self.files:
                    relative_path = Path(root) / filename
                    absolute_path = relative_path.absolute()
                    file_list.append(absolute_path)
        return file_list
