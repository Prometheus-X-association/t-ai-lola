#!/usr/bin/env python3

import pytest
import os

from lolapy.tools import settings
from lolapy.tools import errors


def test_EditSettings():
    """Test the EditSettings object.

    Validate that a variable edited in the context manager does not edit the
    settings outside the context.
    """

    # Do a backup of the environment
    app_settings_backup = settings.get().copy()

    with settings.EditSettings():
        settings.get().http_proxy = "https://8.8.8.8"
        app_settings = settings.get()
        assert app_settings.http_proxy == "https://8.8.8.8"

    app_settings = settings.get()
    assert app_settings == app_settings_backup


@pytest.mark.usefixtures("fixture_env_file_complete")
def test_proxy(fixture_env_file_complete):
    """fixture_env_file create env file with a variable proxy empty"""
    backup_env_file = os.environ["ENV_FILE"]
    os.environ["ENV_FILE"] = str(fixture_env_file_complete)
    settings.AppSettingsBuilder.reset()
    app_settings = settings.get()
    assert app_settings.http_proxy == "this_is_a_fake_proxy"
    os.environ["ENV_FILE"] = backup_env_file


def test_print():
    app_settings = settings.get()
    app_settings.print()


def test_ENV_FILE_not_set():
    backup_env_file = os.environ["ENV_FILE"]
    os.environ.pop("ENV_FILE")
    settings.AppSettingsBuilder.reset()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        settings.get()
    assert pytest_wrapped_e.type == SystemExit
    os.environ["ENV_FILE"] = backup_env_file


def test_ENV_FILE_not_exist():
    backup_env_file = os.environ["ENV_FILE"]
    os.environ["ENV_FILE"] = "/tmp/this_file_not_exists"
    settings.AppSettingsBuilder.reset()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        settings.get()
    assert pytest_wrapped_e.type == SystemExit
    os.environ["ENV_FILE"] = backup_env_file


@pytest.mark.usefixtures("fixture_env_file_missing_variable")
def test_env_missing_variable(fixture_env_file_missing_variable):
    backup_env_file = os.environ["ENV_FILE"]
    os.environ["ENV_FILE"] = str(fixture_env_file_missing_variable)
    settings.AppSettingsBuilder.reset()
    with pytest.raises(errors.SettingsMissingParameters):
        settings.get()
    os.environ["ENV_FILE"] = backup_env_file
