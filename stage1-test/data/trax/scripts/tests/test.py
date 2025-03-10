#!/usr/bin/env python3

from src import env

def test_env_file():
    import tempfile

    tmp_file = """
# Commentary
DOCKER_IMAGE=Debian:buster

# ShouldIgnore=value

 # Strange line
    """

    # Create tmp file
    env_file = tempfile.NamedTemporaryFile(mode = 'w+')
    env_file.write(tmp_file)
    env_file.seek(0)

    my_env_file = env.Env(env_file.name)
    assert my_env_file.get("DOCKER_IMAGE") == "Debian:buster"
    env_file.close()
