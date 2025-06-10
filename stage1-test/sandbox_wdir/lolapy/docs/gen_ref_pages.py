#!/usr/bin/env python3
"""Generate the code reference pages."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path, PosixPath
import os

import jinja2


@dataclass
class DocFile:
    """Structure which hold information on Document File.

    Attributes:
        module_path: Relative Path to the module (exemple "lolapy/algorithm/scripts.py")
        doc_path: Name of the generated markdown file (exemple "scripts.md")
        full_doc_path: Relative full path to the markdown file (exemple "docs/references/lolapy/algorithm/scripts.md")
        imported_module: Full name of the module to importe in Python-style (exemple "lolapy.algorithm.scripts")
    """

    module_path: Path
    full_doc_path: Path
    imported_module: str

    @classmethod
    def from_path(cls, file_path: Path) -> Self:
        """Generate DocFile from py file.

        Args:
            file_path: Path of the py file
        Returns:
            DocFile
        """
        module_path: Path = file_path
        full_doc_path = Path("docs/references") / file_path.relative_to(
            "lolapy"
        ).with_suffix(".md")
        full_module_name = ".".join(list(module_path.parts)).replace(".py", "")
        if full_module_name.endswith(".__init__"):
            full_module_name = full_module_name.replace(".__init__", "")
        return DocFile(
            module_path=module_path,
            full_doc_path=full_doc_path,
            imported_module=full_module_name,
        )

    def is_empty_file(self) -> bool:
        """Test if the file is empty by checking its size.

        Returns:
            True if the file is empty. False otherwise.
        """
        if os.stat(path).st_size == 0:
            return True
        return False


all_doc_files: list[DocFile] = []

for path in sorted(Path("lolapy").rglob("*.py")):
    current_path = DocFile.from_path(path)
    if current_path.is_empty_file():
        # Don't do anything if file is empty
        continue
    if not current_path.full_doc_path.exists():
        # If there is no parents path
        current_path.full_doc_path.mkdir(parents=True)
    with open(current_path.full_doc_path, "w") as full_doc:
        print("::: " + current_path.imported_module, file=full_doc)
    all_doc_files.append(current_path)


class GenMarkdownList:
    """TODO: end this
    https://mkdocstrings.github.io/recipes/#automatic-code-reference-pages
    """

    def __init__(self, files: list[DocFile]):
        self.files: list[DocFile] = files

    def _sort_hierarchically(self) -> dict:
        """Generated nested structures of docfiles to sort files hiearachically."""
        hierarchical_sort = {}
        for docfile in self.files:
            module_parts = docfile.imported_module.split(".")
            current_pos = hierarchical_sort
            for index, ii in enumerate(module_parts):
                if index == len(module_parts) - 1:
                    print("here")
                    current_pos[ii] = docfile
                    break
                if not ii in current_pos:
                    current_pos[ii] = {}
                current_pos = current_pos[ii]
            current_pos = hierarchical_sort
        return hierarchical_sort


# print(GenMarkdownList(all_doc_files)._sort_hierarchically())
# markdown_index_template = Path("docs/index.md")
# with open(markdown_index_template) as f:
#    rendered = jinja2.Template(f.read()).render(**self.parameters)
