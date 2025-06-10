#!/usr/bin/env python3

from enum import Enum, auto
from pathlib import Path

from lolapy.tools import settings

class SbatchScript(Enum):
    START_TRAX = auto()
    START_INIT_TRAX = auto()
    POPULATE_TRAX = auto()

    def get_script(self, **kwargs) -> str:
        """Get the sbatch script according to the enum value.

        Pass arguments to expand scripts. It depends of the script, check methods to see required variables.
        Possible arguments are the following:
        :param job_name: str: name of the job. Used to identify the docker container.
        :param stdout_slurm: Path: Path to the output stdout log for slurm.
        :param stderr_slurm: Path: Path to the output stderr log for slurm.
        :param json_directory: Path: Path to the directory containing splitted json files.
        :param db_host: str: hostname or ip adress of the database server.
        :param database_name: str: Name of the database to use in the container. Usually, it's the database hash.
        :param db_user: str: Username to use for the connection to the SQL server.
        :param db_password: str: Password to use for the connection to the SQL server.
        :param trax_port: int: Port on the cluster of the running Trax container.
        """
        choices = {
            SbatchScript.START_TRAX: self._start_trax_script,
            SbatchScript.START_INIT_TRAX: self._start_init_trax_script,
            SbatchScript.POPULATE_TRAX: self._populate_trax_script,
        }
        return choices[self](**kwargs)

    def _start_trax_script(
        self,
        job_name: str,
        stdout_slurm: Path,
        stderr_slurm: Path,
        db_host: str,
        database_name: str,
        db_user: str,
        db_password: str,
        **kwargs,
    ) -> str:
        """Create a script to start a trax container as service.

        :param job_name: str: name of the job. Used to identify the docker container.
        :param stdout_slurm: Path: Path to the output stdout log for slurm.
        :param stderr_slurm: Path: Path to the output stderr log for slurm.
        :param db_host: str: hostname or ip adress of the database server.
        :param database_name: str: Name of the database to use in the container. Usually, it's the database hash.
        :param db_user: str: Username to use for the connection to the SQL server.
        :param db_password: str: Password to use for the connection to the SQL server.
        :return: str: The sbatch script
        """
        app_settings = settings.get()
        txt = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --cpus-per-task=2
#SBATCH --mem=2G
#SBATCH --output={str(stdout_slurm)}
#SBATCH --error={str(stderr_slurm)}

# Catch all EXIT signal and kill the container.
# It's used to prevent docker daemon to keep container alive
trap "kill_container" EXIT
kill_container() {{
    docker kill {job_name}
}}

docker run --name {job_name} \
-e APP_NAME='TRAX LRS' \
-e APP_ENV=local \
-e APP_KEY=base64:riCU/XELDxWpa3ilrcjjuoIfCuvfMNIaKH4u6/7R4tY= \
-e APP_DEBUG=false \
-e APP_URL=http://localhost \
-e DB_CONNECTION=mysql \
-e DB_HOST={db_host} \
-e DB_PORT=3306 \
-e DB_DATABASE={database_name} \
-e DB_USERNAME={db_user} \
-e DB_PASSWORD={db_password} \
-e DB_MARIADB=0 \
-e SESSION_DRIVER=database \
-e SESSION_CONNECTION=mysql \
-e SESSION_LIFETIME=240 \
--publish-all {app_settings.trax_image_client}
"""
        return txt

    def _start_init_trax_script(
        self,
        job_name: str,
        stdout_slurm: str,
        stderr_slurm: str,
        db_host: str,
        database_name: str,
        db_user: str,
        db_password: str,
        **kwargs,
    ) -> str:
        """Create a script to start a trax container and initiate the trax database inside.

        :param job_name: str: name of the job. Used to identify the docker container.
        :param stdout_slurm: Path: Path to the output stdout log for slurm.
        :param stderr_slurm: Path: Path to the output stderr log for slurm.
        :param db_host: str: hostname or ip adress of the database server.
        :param database_name: str: Name of the database to use in the container. Usually, it's the database hash.
        :param db_user: str: Username to use for the connection to the SQL server.
        :param db_password: str: Password to use for the connection to the SQL server.
        :return: str: The sbatch script
        """
        app_settings = settings.get()
        txt = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --cpus-per-task=2
#SBATCH --mem=2G
#SBATCH --output={stdout_slurm}
#SBATCH --error={stderr_slurm}

set -ueo pipefail

# Catch all EXIT signal and kill the container.
# It's used to prevent docker daemon to keep container alive
trap "kill_container" EXIT
kill_container() {{
    docker kill {job_name}
    quit=1
}}

run_in_docker() {{
    docker exec {job_name} bash -c "$@"
}}

docker run --name {job_name} \
--detach \
-e APP_NAME='TRAX LRS' \
-e APP_ENV=local \
-e APP_KEY=base64:riCU/XELDxWpa3ilrcjjuoIfCuvfMNIaKH4u6/7R4tY= \
-e APP_DEBUG=false \
-e APP_URL=http://localhost \
-e DB_CONNECTION=mysql \
-e DB_HOST={db_host} \
-e DB_PORT=3306 \
-e DB_DATABASE={database_name} \
-e DB_USERNAME={db_user} \
-e DB_PASSWORD={db_password} \
-e DB_MARIADB=0 \
-e SESSION_DRIVER=database \
-e SESSION_CONNECTION=mysql \
-e SESSION_LIFETIME=240 \
--publish-all {app_settings.trax_image_admin}

sleep 5  # prevent job not run
run_in_docker "php /var/www/html/traxlrs/artisan migrate --force"
run_in_docker "php /var/www/html/traxlrs/artisan client:create"

quit=0
while [ "$quit" -ne 1 ]; do
    printf 'Trax for populating is running. Kill job to kill trax service'
    date
    sleep 30
done
"""
        return txt

    def _populate_trax_script(
        self,
        job_name: str,
        stdout_slurm: str,
        stderr_slurm: str,
        json_directory: Path,
        trax_port: int,
        **kwargs,
    ) -> str:
        """Create a script to populate a trax database with curls.

        :param job_name: str: name of the job. Used to identify the docker container.
        :param stdout_slurm: Path: Path to the output stdout log for slurm.
        :param stderr_slurm: Path: Path to the output stderr log for slurm.
        :param json_directory: Path: Path to the directory containing splitted json files.
        :param trax_port: int: Port on the cluster of the running Trax container.
        :return: str: The sbatch script
        """

        txt = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --cpus-per-task=2
#SBATCH --mem=2G
#SBATCH --output={stdout_slurm}
#SBATCH --error={stderr_slurm}

number_total_file=$(ls {str(json_directory)})
index_current_file=0
for json_file in $(ls {str(json_directory)}); do
    # Use -sS option to hide progress-bar and avoid curl to write progress to stderr wich causes catch error
    curl -sS --location --request POST "0.0.0.0:{trax_port}/trax/ws/xapi/statements" \
        --header 'X-Experience-API-Version: 1.0.3' \
        --header 'Accept: application/json' \
        --header 'Authorization: Basic dGVzdHN1aXRlOnBhc3N3b3Jk' \
        --header 'Content-Type: application/json' \
        --data "@{str(json_directory)}/${{json_file}}"
    index_current_file=$((index_current_file+1))
    echo "DONE file ${{current_file}}/${{number_total_file}}"
done
"""
        return txt
