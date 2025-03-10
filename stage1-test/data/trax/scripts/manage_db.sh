#!/usr/bin/env bash
set -o pipefail

##  a new mysq database in a Docker container

cmdname=$(basename "$0")
fullpath=$(realpath "$0")

usage() {
  yellow=$(tput setaf 3)
  green=$(tput setaf 2)
  normal=$(tput sgr0)

  cat >&2 << USAGE
${green}Create database${normal} from trax recipe
Create a new database in running MySQL server.
MYSQL_ROOT_PASSWORD env variable must be set or working directory with -w/--workdir option containing .env file must be set.

${green}Usage:${normal}
        $cmdname COMMAND <SUBCOMMAND>

${green}Command:${normal}
        ${yellow}--create${normal}                 Create the database
        ${yellow}--remove${normal}                 Remove the database
        ${yellow}--list${normal}                   list databases
        ${yellow}--populate${normal}               populate database. -j/--json option must be used
                                 with this command

${green}Subcommands:${normal}
        ${yellow}-h, --help${normal}               Print this help message

        ${yellow}-e, --env <PATH>${normal}         Path of the .env file if the variable ENV_FILE is not set
        ${yellow}-d, --dbname <NAME>${normal}      Name of the database to create.
        ${yellow}-j, --json <PATH>${normal}        Path of the json file. Used with --populate command

USAGE
}

function die() {
  echo >&2 "$cmdname: [Err] $*"
  exit 1
}

function populate_db() {
  set -uex
  container_name="trax_${databaseName}_${RANDOM}"
  docker-compose -f ${ROOT_DIR}/docker-compose.yml run -d -v ${jsonFile}:/xapi.json \
    -v "${TRAX_ENV}/:/var/www/html/traxlrs/.env" \
    -e DB_DATABASE=${databaseName} \
    --name ${container_name} ${DOCKER_TRAX_ADMIN_NAME}
  docker exec -w /var/www/html/traxlrs ${container_name} php artisan client:create
  docker exec ${container_name} curl --location \
    --request POST 'localhost:80/trax/ws/xapi/statements' \
    --header 'X-Experience-API-Version: 1.0.3' --header 'Accept: application/json' \
    --header 'Authorization: Basic dGVzdHN1aXRlOnBhc3N3b3Jk' \
    --header 'Content-Type: application/json' -d '@/xapi.json'
  docker stop ${container_name}
  docker rm ${container_name}
  exit 0
}


SHORT=,d:,h,,j:,e:
LONG=list,create,remove,populate,help,dbname:,json:,env:

TEMP=$(getopt --options $SHORT --long $LONG -n $"cmdname" -- "$@")

## If no argument provide, print help
if [ $# -eq 0 ]; then
usage
exit 0
fi

envFile=
databaseName=""
createCMD=0
removeCMD=0
listCMD=0
populateCMD=0
jsonFile=""

eval set -- "$TEMP"
while true; do
    case "$1" in
    -h|--help) usage; exit 0 ;;
    --create) createCMD=1; shift ;;
    --remove) removeCMD=1; shift ;;
    --list) listCMD=1; shift ;;
    --populate) populateCMD=1; shift ;;
    -e|--env ) envFile="$2"; shift 2 ;;
    -d|--dbname) databaseName="$2"; shift 2 ;;
    -j|--json) jsonFile="$(realpath $2)"; shift 2;;
    -- ) shift; break ;;
    * ) die "$1: unexpected" ;;
  esac
done

## Check if only one command is used
sumCommand=$((createCMD+removeCMD+listCMD+populateCMD))
[ $sumCommand -eq 1 ] || die "Use one command between --create, --remove, --list or --populate"

## Check if all subcommands are provided
[ -z "${ENV_FILE}" ] && [ -z "${envFile}" ] && die "Please set ENV_FILE variable or use -e/--env"
[ -z "$databaseName" ] && [ $listCMD -ne 1 ] && die "Please set a database name (-d/--dbname)"
[ -z "$jsonFile" ] && [ $populateCMD -eq 1 ] && die "Please set a json file with -j/--json option"

## Export env variables
[ -z "${envFile}" ] && envFile="${ENV_FILE}"
export $(grep -v '^#' "$envFile" | xargs)

[ -z "$MYSQL_ROOT_PASSWORD" ] && die "MYSQL_ROOT_PASSWORD variable not set in env"

[ $populateCMD -eq 1 ] && populate_db

mySQLQuery=""
[ $createCMD -eq 1 ] && mySQLQuery="CREATE DATABASE ${databaseName}"
[ $removeCMD -eq 1 ] && mySQLQuery="DROP DATABASE ${databaseName}"
[ $listCMD -eq 1 ] && mySQLQuery="SHOW DATABASES"

docker exec -u root:root "${COMPOSE_DB_NAME}" /usr/bin/mysql -uroot --password=${MYSQL_ROOT_PASSWORD} --execute="${mySQLQuery}"
