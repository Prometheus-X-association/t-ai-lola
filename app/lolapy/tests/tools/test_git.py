#!/usr/bin/env python3

"""Module to test the GIT module of lolapy"""

from pathlib import Path

import pytest

from lolapy.tools import settings
from lolapy.tools.git import GitRepo
from lolapy.tools import errors as tools_errors

url = "https://github.com/EbookFoundation/free-programming-books"
tag = "main"


@pytest.mark.slow
@pytest.mark.usefixtures("fixture_GitRepo_clone_empty_dir")
def test_GitRepo_clone_empty_dir(fixture_GitRepo_clone_empty_dir):
    """Test if the clone of a repository success"""
    git_repo = GitRepo(
        git_repo=url, destination=Path(fixture_GitRepo_clone_empty_dir), git_tag=tag
    )
    with settings.EditSettings():
        settings.get().http_proxy = None
        git_repo.clone()


@pytest.mark.slow
@pytest.mark.usefixtures("fixture_GitRepo_clone_full_dir")
def test_GitRepo_clone_full_dir(fixture_GitRepo_clone_full_dir):
    """Test if the clone of a repository fails if the destination is not empty"""
    git_repo = GitRepo(
        git_repo=url, destination=Path(fixture_GitRepo_clone_full_dir), git_tag=tag
    )
    with (
        pytest.raises(tools_errors.GitCloneDestionnationError) as e,
        settings.EditSettings(),
    ):
        settings.get().http_proxy = None
        git_repo.clone()


@pytest.mark.slow
@pytest.mark.usefixtures("fixture_GitRepo_clone_create_dir")
def test_GitRepo_clone_non_existing_dir(fixture_GitRepo_clone_create_dir):
    """Test if the clone of a repository can create the non-existing destination"""
    git_repo = GitRepo(
        git_repo=url, destination=Path(fixture_GitRepo_clone_create_dir), git_tag=tag
    )
    with settings.EditSettings():
        settings.get().http_proxy = None
        git_repo.clone()


@pytest.mark.slow
@pytest.mark.usefixtures("fixture_GitRepo_clone_empty_dir")
def test_GitRepo_clone_non_existing_branch(fixture_GitRepo_clone_empty_dir):
    """Test if the clone of a repository fails if the branch does not exists"""
    git_repo = GitRepo(
        git_repo=url,
        destination=Path(fixture_GitRepo_clone_empty_dir),
        git_tag="blablablibli",
    )
    with (pytest.raises(tools_errors.GitCloneError), settings.EditSettings()):
        settings.get().http_proxy = None
        git_repo.clone()


@pytest.mark.slow
@pytest.mark.usefixtures("fixture_GitRepo_clone_dest_no_permission")
def test_GitRepo_clone_permission_denied(fixture_GitRepo_clone_dest_no_permission):
    """Test if the clone of a repository fails if the branch does not exists"""
    git_repo = GitRepo(
        git_repo=url,
        destination=Path(fixture_GitRepo_clone_dest_no_permission),
        git_tag=tag,
    )
    with (
        pytest.raises(tools_errors.GitCloneDestionnationError),
        settings.EditSettings(),
    ):
        settings.get().http_proxy = None
        git_repo.clone()
