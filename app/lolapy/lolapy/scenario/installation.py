#!/usr/bin/env python3

"""Module to manage installation of scenario.

On the frontend application, user can add scenario. The frontend send a request to lolapy
with the following information

```json
{
  "scenario_url_repository": "https://gitlab.inria.fr/test",
  "tag_name": "nomdutag",
  "tag_hash": "6b9eb5f45aba1fc2d6467647be760868d7a2b31e"
}
```

tag_hash is the unique name of the scenario. All scenario are stored in the same folder defined in
the environment variable ${NEXTFLOW_SCENARIO_DIR}. The tag_hash is the name of the directory containing
the installed scenario.

Lolapy must:
- download scenario from git repo
- switch to the good tag name
- validate the scenario

The entrypoint of this module is the InstallScenario object

How to use
```
from scenario.installation import InstallScenario

post_data = {
  "repository": "git@gitlab.inria.fr:lola/scenarios/template-scenario.git",
  "tag_name": "1.1.0",
  "tag_hash": "AUYTDHUAYTDBSTDSQIFYTBIQSFTQSYFTQBYF",
}

InstallScenario.install(repository_url=post_data["repository"],
                        tag_name=post_data["tag_name"],
                        tag_hash=post_data["tag_hash"])

InstallScenario.check(tag_hash)
InstallScenario.delete(tag_hash)
```

"""

from __future__ import annotations
from attr import dataclass
import logging
import shutil

from lolapy.tools import git
from lolapy.tools import docker
from lolapy.tools import frontend_api
from lolapy.scenario import errors as scenario_errors
from lolapy.scenario.scenario import Scenario


@dataclass
class InstallScenario:
    """Class to fetch online the scenario

    Attributes:
        repository_url: Url of the git repository
        tag_name: Git tag to use when download repository
        hash: Hash unique of the scenario
        scenario: Instance of Scenario. BE CAREFUL, this scenario is not verified and
            is just used for path generation (Scenario generate scenario_path, scenario_recipe_path, etc ...)
        """
    repository_url: str
    tag_name: str
    hash: str
    scenario: Scenario

    @classmethod
    def build(cls, repository_url: str, tag_name: str, hash: str) -> Self:
        """Constructor for InstallScenario.

        Args:
            repository_url: Url of the git repository
            tag_name: Git tag to use when download repository
            hash: Hash unique of the scenario
        Returns:
            InstallScenario: an instance of InstallScenario
        """
        return cls(
            repository_url=repository_url,
            tag_name=tag_name,
            hash=hash,
            scenario=Scenario.from_hash(scenario_hash=hash, check_exists=False)
        )

    def install(self):
        """Install a new Nextflow scenario.

        """
        # Create the scenario directory
        self._create_scenario_directory()
        # clone scenario repository
        git.GitRepo(
            git_repo=self.repository_url,
            git_tag=self.tag_name,
            destination=self.scenario.scenario_path,
        ).clone()
        # Validate the scenario
        scenario_verified: Scenario = Scenario.from_hash(scenario_hash=self.hash, check_exists=True)
        # Download docker dependencies
        docker_images_list = scenario_verified.scenario_recipe.docker_images  # scenario_recipe is not None
        # Sanitize URL of docker images
        for image in docker_images_list:
            image.sanitize()
        #docker.PullDockerImages(docker_images=docker_images_list).pull()
        # everything is Done. Log complete to the frontend
        frontend_api.FrontendRequest.get(url=f"/api/tag/{self.hash}/complete")

    @staticmethod
    def remove(scenario_hash: str):
        """Remove an installed scenario

        Args:
            scenario_hash: Hash unique of the scenario
        Raise:
            scenario_errors.ScenarioNotExist: if the scenario does not exist.
        """
        # Don't check if the scenario is a valid scenario. This method can be used to remove
        # unvalid scenario
        my_scenario = Scenario.from_hash(scenario_hash=scenario_hash, check_exists=False)
        if my_scenario.scenario_path.is_dir():  # handle exists() in is_dir()
            shutil.rmtree(my_scenario.scenario_path)
        else:
            raise scenario_errors.ScenarioNotExist(my_scenario.scenario_path)
        # TODO: log this outside of the method
        frontend_api.FrontendRequest.log(f"{scenario_hash} scenario removed")

    def _create_scenario_directory(self) -> None:
        """Check if the destination path is available and create it.

        Raises:
            InstallationDirNotEmpty: If the directory where to install scenario is not empty
        """
        if self.scenario.scenario_path.is_dir():  # handle if dir exists too
            if len(list(self.scenario.scenario_path.glob("*"))):  # If directory is not empty
                raise scenario_errors.InstallationDirNotEmpty(self.scenario.scenario_path)
        else:
            # Use parents=True to create the full dir tree if it does not exist
            # exist_ok raise an error if dir already exists -> avoid collision between scenarios
            self.scenario.scenario_path.mkdir(parents=True, exist_ok=True)
            logging.debug(f"Create '{self.scenario.scenario_path}' to clone scenario")

