#!/usr/bin/env python3

"""Module used to check everything on the startup of the application"""

from lolapy.tools import settings
from lolapy.tools import errors as tools_errors

from lolapy.tools.shell_command import ShellCommand, CommandResult

class CheckInstallation:
    @staticmethod
    def check():
        CheckTraxImages.check_trax_images()

class CheckTraxImages:
    @classmethod
    def check_trax_images(cls):
        app_settings = settings.get()
        trax_images = (app_settings.trax_image_client, app_settings.trax_image_admin)
        for image in trax_images:
            if not cls.check_image(image):
                raise tools_errors.TraxImageNotFound(image)

    @staticmethod
    def check_image(image_name: str) -> bool:
        """Check if the docker image is present on the cluster server.

        Args:
            image_name: str: Name of the docker image.
        Returns:
            bool: True if the image is present, False if not present.
        """
        # Run the docker images command and filter with image name
        # -q to only keep images ID
        command_result = ShellCommand.from_env(command=f"docker images -q {image_name}").run()
        if len(command_result.stdout.splitlines()) >= 1:
            return True
        return False
