# Frontend application

## Requirements
Works with these versions. Older versions may work but have not be tested.
- docker >= 19.03.13
- docker-compose >= 1.25.4

## How to build images

```bash
$ git clone http://gitlab.inria.fr/lola/frontend
$ cd frontend
$ make env_sf
$ make build
$ docker images | grep frontend 
frontend               latest          5ca305886847   About a minute ago   1.07GB
```

## How to use (Production)

```bash
$ git clone http://gitlab.inria.fr/lola/frontend
$ cd frontend

# Generate a .env file from the .env.sample with your own parameters

# Start the application with
$ make up

# Initialize the database for production environment (minimal dataset)
$ make app_db_fixture_prod

```

## How to use (Development)

```bash
$ git clone http://gitlab.inria.fr/lola/frontend
$ cd frontend

# Generate a .env file from the .env.sample with your own parameters

# Start the application with
$ make up_dev

# Initialize the database for development environment (full dataset)
$ make app_db_fixture_dev

```


## Defaults user for development environment

|      User     |           Role           |  
|:-------------:|:------------------------:|
|   p1@lola.fr  |         profile 1        |
|   p2@lola.fr  |         profile 2        |
|   p3@lola.fr  |         profile 3        |
|   p4@lola.fr  |         profile 4        |
|   p5@lola.fr  |         profile 5        |
|  sisr@lola.fr | Admin SISR (logs access) |
| admin@lola.fr |     Admin, profile 4     |

Password = azerty  
All user are 'active'

## Defaults user for production environment

|      User     |           Role           |  
|:-------------:|:------------------------:|
|  sisr@lola.fr | Admin SISR (logs access) |

Password = azerty  
The sisr@lola.fr user is 'active'

## Default web access
- Application : http://localhost:81
- Phpmyadmin : http://localhost:8181
- Doc API : http://localhost:81/api/doc
