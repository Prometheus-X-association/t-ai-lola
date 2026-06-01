#!/usr/bin/env python3

import cryptncompress.compress


def compress(lst_files, output_archive):
    my_zip = cryptncompress.compress.Compress(
        output_archive=output_archive
    )
    my_zip.compress(lst_files)


def extract(input_archive, output_directory):
    files_in_archive = None
    my_zip = cryptncompress.compress.Extract(
        archive=input_archive,
        output_dir=output_directory,
        files_in_archive=files_in_archive,
    )
    my_zip.extract()
