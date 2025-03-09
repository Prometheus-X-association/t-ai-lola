#!/usr/bin/bash

## Start a trax service with a specific database and on specific port

cmdname=$(basename "$0")
fullpath=$(realpath "$0")

OUTPUTSTREAM=/dev/null

usage() {
  yellow=$(tput setaf 3)
  green=$(tput setaf 2)
  normal=$(tput sgr0)

  cat >&2 << USAGE
${green}Start trax${normal} from trax recipe
Start a trax server with a specific database and on specific port

${green}Usage:${normal}
        $cmdname COMMAND name <SUBCOMMAND> <OPTIONS>

${green}Commands:${normal}
        ${yellow}--stop <CONTAINER NAME>${normal}         Stop a specific instance of trax based on name
        ${yellow}--start <CONTAINER NAME>${normal}        Start a trax instance with a specific database
        ${yellow}--gen_admin <CONTAINER NAME>${normal}    Generate a admin in the running container

${green}Subcommands for --start:${normal}
        ${yellow}-p, --port <NAME>${normal}     Port number of the service (Optionnal. Script can found open port)
        ${yellow}-d, --dbname <NAME>${normal}   Name of the database to use.
        ${yellow}--writable ${normal}           Allow to edit the database with POST request on xapi

${green}Option:${normal}
        ${yellow}-e, --env <PATH>${normal}      Path of the .env file if the variable ENV_FILE is not set

        ${yellow}-h, --help${normal}            Print this help message
        ${yellow}-v, --verbose${normal}         Enable the verbose mode
USAGE
}

function die() {
  echo >&2 "$cmdname: [Err] $*"
  exit 1
}

function init_db() {
  ## Initialise the database for trax
  ##
  ## $1: name of the container

  CONTAINER_NAME="$1"
  docker exec -w /var/www/html/traxlrs ${CONTAINER_NAME} php artisan migrate --force
}

function find_available_port() {
  ## Search through docker ps to find a available port by starting at 8080
  ## Return as text the available port number
  declare -a ports
  ports+=("$(docker ps --format '{{.Ports}}' | grep : | cut -d ':' -f 2 | cut -d '-' -f 1)")
  local new_port=8080
  local good_port=0
  while [ $good_port -eq 0 ]; do
    new_port=$((new_port+1))
    good_port=1
    for port in $(echo $ports); do ## iterate through know port
      [ $port -eq $new_port ] && good_port=0
    done
  done
  echo $new_port
}


## Set working directory to the root of the project
OLDDIR=$(pwd)
cd $(dirname "$fullpath")/..

trap 'catch' EXIT
catch() {
  cd "$OLDDIR"
}

SHORT=p:,d:,e:,h,v
LONG=start:,stop:,gen_admin:,port:,env:,dbname:,help,verbose,writable

TEMP=$(getopt --options ${SHORT} --long ${LONG} -n $"cmdname" -- "$@")

## If no argument provide, print help
if [ $# -eq 0 ]; then
usage
exit 0
fi

portNumber=
databaseName=
containerName=
startCMD=0
stopCMD=0
gen_adminCMD=0
writable=0
env_file=

eval set -- "$TEMP"
while true; do
  case "$1" in
    --start) startCMD=1; containerName="$2"; shift 2 ;;
    --stop) stopCMD=1; containerName="$2"; shift 2 ;;
    --gen_admin) gen_adminCMD=1; containerName="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    -p|--port) portNumber="$2"; shift 2 ;;
    -d|--dbname ) databaseName="$2"; shift 2 ;;
    -e|--env ) env_file="$2"; shift 2 ;;
    -v|--verbose ) OUTPUTSTREAM="/dev/stdout"; shift ;;
    --writable) writable=1; shift ;;
    -- ) shift; break ;;
    * ) die "$1: unexpected" ;;
  esac
done


## Check if only one command is used
sumCommand=$((startCMD+stopCMD+gen_adminCMD))
[ $sumCommand -eq 1 ] || die "Use one command between --start, --stop or --gen_admin"

[ $stopCMD -eq 1 ] && docker stop $containerName && docker rm $containerName && echo "Stopped container: ${containerName}" && exit 0
[ $gen_adminCMD -eq 1 ] && docker exec -w /var/www/html/traxlrs/ $containerName php artisan user:create-admin && exit 0

## Check if all subcommands are provided
[ -z "${ENV_FILE}" ] && [ -z "${env_file}" ] && die "Please set ENV_FILE variable or use -e/--env"
[ -z "$portNumber" ] && portNumber=$(find_available_port)
[ -z "$databaseName" ] && die "Please set a database name (-d/--dbname)"

## Export env variables
[ -z "${env_file}" ] && env_file="${ENV_FILE}"
export $(grep -v '^#' "$env_file" | xargs)

## Docker image to use
dockerImage=${DOCKER_TRAX_CLIENT_NAME} # Disable POST request
[ $writable -eq 1 ] && dockerImage=${DOCKER_TRAX_ADMIN_NAME}


# docker-compose return the name of the service after creation
service_name=$(docker-compose \
  -f docker-compose.yml\
  -f docker-compose-client.yml\
  run --rm -d -p 127.0.0.1:${portNumber}:80 \
  --name ${containerName} \
  -v "${TRAX_ENV}:/var/www/html/traxlrs/.env" \
  -e DB_DATABASE=${databaseName} ${dockerImage})


# If the service is started, run the command to initialise the database
# The commande did nothing if the database is already initialised
if [ $? -eq 0 ]; then
  init_db "$service_name" >> ${OUTPUTSTREAM}
else
  echo $service_name
  die "Something wrong append during container creation."
fi
