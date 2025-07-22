#!/usr/bin/env python3

r"""
LolapyGlobalError
│
└── slurmerrors
    │
    ├── JobInfoErrors
    │   ├── jobinfomissingjob
    │   └── jobinfofielderror
    │
    └── slurmtraxerrors
        └── traxunreachable
"""

from lolapy.errors import LolapyGlobalError


class SlurmErrors(LolapyGlobalError):
    """Main error for Slurm problems"""

    pass


class JobInfoErrors(SlurmErrors):
    """Main error for sacct parsing command"""

    pass


class JobInfoMissingJob(JobInfoErrors):
    """Error raising when no job can be founded"""

    def __init__(self, job_name: str):
        self.message = f"'{job_name}' cannot be found with sacct command"
        self.public_message = LolapyGlobalError.standard_public_message


class JobInfoFieldError(JobInfoErrors):
    """Error when trying to get wrong field with sacct command"""

    def __init__(self, field: str):
        self.message = (
            f"Field '{field}' is not available and cannot be parse from sacct output"
        )
        self.public_message = LolapyGlobalError.standard_public_message


class SbatchErrors(SlurmErrors):
    """Main error for sbatch script problems"""

    pass


class SbatchMissingValueError(SbatchErrors):
    """Error when missing variable when creating sbatch script"""

    def __init__(self, missing_variable: str):
        self.message = (
            f"Missing variable '{missing_variable}' when templating sbatch script"
        )
        self.public_message = LolapyGlobalError.standard_public_message


class SbatchImportDataset(SbatchErrors):
    """Unknow error with slurm during import of dataset"""

    def __init__(self, job_name: str):
        self.message = (
            f"Unknow error with slurm job '{job_name}' during importing Trax dataset"
        )
        self.public_message = LolapyGlobalError.standard_public_message


class SlurmTraxErrors(SlurmErrors):
    """Main error for slurm trax."""

    pass


class TraxUnreachable(SlurmTraxErrors):
    """Error when getting Trax Docker port."""

    def __init__(self, stderr: str):
        self.message = f"Error when getting trax docker port: {stderr}"
        self.public_message = LolapyGlobalError.standard_public_message
