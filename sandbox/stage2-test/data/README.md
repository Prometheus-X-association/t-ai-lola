# Description

This project allows you to set up, in a docker container, 
an LRS based on the starter version of [TRAX3](https://github.com/trax-project/trax3-starter-lrs)
with a *mysql* datase.

The project leverages Docker and Makefile automation to streamline 
setup and operations, ensuring a reproducible environment across 
different systems (Ununtu and MacOS). 
Docker encapsulates all dependencies within containers, 
simplifying management and deployment, 
while Makefiles automate repetitive tasks such as 
building, running, and testing the application. 


# Requirements

The project requires the following software to be installedbefore installing
*trax-lola*: 

- docker (>= 20.10.18): Necessary for containerization. 
Installation instructions are available on the Docker website 
((see [Docker - installation](https://docs.docker.com/get-docker/))).
- docker-compose (>= 1.29.2): 
Required for managing multi-container Docker applications.
- make (>= 4.2.1): Required for running Makefiles.
Make is typically pre-installed on Unix-based systems.
For Windows, you can install Make using the MinGW toolset ((see [MinGW](http://www.mingw.org/))).

# Installation & Setup

**Clone the repository**

```
git clone https://github.com/azim54/trax3-lola.git
```
# Configuration

**.env file**

The .env file contains the environment variables required for 
the Trax LRS setup. The file is located in the trax3-lola directory.

The following environment variables must be adapted in 
the .env file:
```
DATABASE_NAME=traxdb        # Database name
MYSQL_ROOT_USER=root        # MySQL root user
MYSQL_ROOT_PASSWORD=root    # MySQL root password
DB_DATA_DIR=./database      # Database data directory
MYSQL_USER=azim             # MySQL user
MYSQL_PASSWORD=root         # MySQL user password
```
** .env.trax file**

The .env.trax file contains the environment variables
used by Trax3 distribution
The file is also located in the trax3-lola directory.

```
DB_CONNECTION=mysql #do not change
DB_HOST=db          #do not change
DB_PORT=3306        #do not change
DB_DATABASE=traxdb  #must be the same as .env file
DB_USERNAME=azim    #must be the same as .env file
DB_PASSWORD=root    #must be the same as .env file

ADMIN_EMAIL=azim@loria.fr   #the name of trax3 user
ADMIN_PASSWORD=root         #the password of trax3 user
```
# Running instructions

Before proceeding, ensure that the Docker daemon is active.

## 1. Trax installation

Run the following command in the project root directory:

```
cd trax3-lola
make up
make trax_initdb
```

This command:
- starts Trax LRS using docker-compose
- initializes the database for Trax LRS

To confirm that the database has been successfully created, 
please navigate to http://localhost:8080 (with phpMyAdmin).
