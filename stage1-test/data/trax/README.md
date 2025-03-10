# TRAX LRS installation and data upload

This document explains how to set up the TRAX Learning Record Store (LRS) and upload dataset files (xAPI statements).
TRAX is a Laravel-based xAPI Learning Record Store used to store and manage learning data.

## Directory main structure
```
/data/trax
│── docker-compose.yml      # Configuration for TRAX LRS and database
│── Makefile                # Automation script for setting up TRAX LRS
│── .env                    # Environment variables for TRAX
│── /dataJson               # Directory containing the dataset (oulad-data.json)

```

## Installation & Setup

**Install TRAX LRS**

TRAX LRS runs inside Docker. To install and start it:

```
cd data/trax
make up
```

This command: 
- starts TRAX LRS (via Docker Compose)
- sets up a MySQL database
- creates admin and client users for authentication
- upload data to TRAX LRS

To verify, check running containers:

```
docker ps
```
Expected result:

```
CONTAINER ID   IMAGE          STATUS              PORTS                 NAMES
xxxxx          trax_trax      Up 1 minute        0.0.0.0:80->80/tcp     trax_trax
xxxxx          mysql:8.0      Up 1 minute        0.0.0.0:3306->3306/tcp trax_db
xxxxx          phpmyadmin     Up 1 minute        0.0.0.0:8080->80/tcp   trax_phpmyadmin
```

**Verify upload**

Log in to TRAX via http://localhost:80, then:
- Navigate to `Statements`
- You should see oulad-data.json loaded

## Manual commands (if needed)

|           Command             |          Description                  |
| ----------------------------- | ------------------------------------- |
|    make up                    |   Start Trax LRS & upload dataset     |
|    make trax_initdb           |   Initialize the database             |
|    make trax_create_client    |	Create a client for API access      |
|    make trax_create_admin     |	Create an admin user                |
|    make upload_data           |	Upload the OULAD dataset            |
|    make logs                  |	View logs                           |
|    make restart               |	Restart TRAX                        |
|    make bash                  |	Open a shell inside TRAX            |
|    make freshstart            |	WARNING: Reset everything           |


## Notes
- ensure Docker is running before installing TRAX
- data is stored in the MySQL database (trax_db container)
- use phpMyAdmin (http://localhost:8080) to check the database manually
