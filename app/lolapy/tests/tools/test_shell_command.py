#!/usr/bin/env python3

from pathlib import Path

import pytest

from lolapy.tools import shell_command
from lolapy.tools import settings
from lolapy.tools import errors

def test_command_localhost():
    cmd_result = shell_command.ShellCommand.new(command="ls -l", on_localhost=True).run()
    assert "tests" in cmd_result.stdout
    assert cmd_result.exit_code == 0

def test_command_localhost_cwd():
    cmd_result = shell_command.ShellCommand.new(command="ls -l", on_localhost=True, work_dir=Path("/etc")).run()
    assert "passwd" in cmd_result.stdout
    assert cmd_result.exit_code == 0

def test_command_localhost_not_background():
    cmd_result = shell_command.ShellCommand.new(command="ls -l", on_localhost=True, background=False, work_dir=Path("/etc")).run()
    assert cmd_result.stdout is None
    assert cmd_result.exit_code == 0

def test_command_not_server_not_localhost():
    with pytest.raises(NotImplementedError):
        _ = shell_command.ShellCommand.new(command="ls -l", on_localhost=False, server=None).run()

def test_command_on_server_from_env():
    with settings.EditSettings():
        settings.get().cluster_host = "localhost"
        settings.get().cluster_is_backend = False
        cmd_result = shell_command.ShellCommand.from_env(command="ls -la").run()
        assert ".bashrc" in cmd_result.stdout
        assert cmd_result.exit_code == None

def test_command_localhost_from_env():
    with settings.EditSettings():
        settings.get().cluster_host = "localhost"
        settings.get().cluster_is_backend = True
        cmd_result = shell_command.ShellCommand.from_env(command="ls -la").run()
        assert "tests" in cmd_result.stdout
        assert cmd_result.exit_code == 0

def test_command_error_ssh():
    with settings.EditSettings():
        settings.get().cluster_host = "999.0.9.0"  # Unknow ip adress
        settings.get().cluster_is_backend = False
        with pytest.raises(errors.SSHConnectionError):
            cmd_result = shell_command.ShellCommand.from_env(command="ls -la").run()

def test_command_ssh_cwd():
    with settings.EditSettings():
        settings.get().cluster_host = "localhost"
        settings.get().cluster_is_backend = True
        cmd_result = shell_command.ShellCommand.new(
            command="ls -la",
            on_localhost=False,
            server=settings.get().cluster_host,
            work_dir=Path("/etc")
        ).run()
        assert "passwd" in cmd_result.stdout
        assert cmd_result.exit_code == None
