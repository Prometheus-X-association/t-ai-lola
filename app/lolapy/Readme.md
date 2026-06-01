# Lolapy

Python API to manage trax in Lola project.

**Documentation of the API**: [Lolapy API Doc](docs/swagger.yaml)

[[_TOC_]]

## Requirements

- python==3.12
- pip==20.3.3
  
You have to install all required packages with python. Use pip and requirements.txt to do it:
```bash
$ pip install -r requirements.txt
```

### Connection requirements

A ssh connection must be available between the backend server where lolapy is installed and the cluster.

## Usage

```bash
git clone https://gitlab.inria.fr/lola/back-end/lolapy
cd lolapy
```
Set the environment variable `ENV_FILE` file to target an environment file containing all required variables. You can use the file `.env.sample`.

```bash
# Copy .env.sample
cp .env.sample .env

# Edit all required variables
vim .env

export ENV_FILE=my_file1
# or with multiple files
export ENV_FILE=my_file1:my_file2
```

### Run in Debug mode (with Flask)

Start the Queue server before.
```bash
$ ls
docs lolapy Readme.md requirements.txt
$ huey_consumer lolapy.bin.async_tasks.huey -w 1
```

Start lolapy
```bash
$ python -m lolapy.bin.app
```

### Production mode
All commands must be executed in the root dir of the project.  

Start the Queue server before.
```bash
$ huey_consumer lolapy.bin.async_tasks.huey -w 1
```

Start lolapy
```bash
$ gunicorn --workers=2 --bind 0.0.0.0:5000 lolapy.bin.wsgi:flask_app
```

## Developpers info

### Deployer les dépendances sur un serveur sans internet avec conda-pack

1. Générer un environnement contenant toutes les dépendances Python avec conda-pack
```bash
$ conda install conda-pack

## Création de l'environnement python contenant les dépendances
$ conda create -n lolapy python=3.12
$ conda activate lolapy
$ pip install -f requirements.txt

## Génération d'une archive tar contenant toutes les dépendances python
$ conda pack -n lolapy -o /tmp/lolapy.tar.gz
```
2. Transférer l'archive sur le serveur
```bash
$ scp /tmp/lolapy.tar.gz lolauser@mon_server:
```
3. Sur le serveur, décompressez l'archive
```bash
$ mkdir $HOME/python-env
$ tar xvf lolapy.tar.gz --directory=python-env
```
4. Ajouter l'archive au Path dans le bashrc
```bash
$ echo 'source \$HOME/python-env/bin/activate' >> ~/.bashrc
$ . .bashrc
```
5. Tester l'import
```bash
$ python -c "import flask"
```

### Uploader l'environnement conda généré à l'aide de conda-pack

1. Générer un environnement contenant toutes les dépendances Python avec conda-pack
```bash
$ conda install conda-pack

## Création de l'environnement python contenant les dépendances
$ conda create -n lolapy_conda python=3.12
$ conda activate lolapy_conda
$ pip install -f requirements.txt

## Génération d'une archive tar contenant toutes les dépendances python
$ conda pack -n lolapy_conda -o /tmp/lolapy_conda.tar.gz
```
2. Envoyer l'archive sur gitlab

Vérifier que le numéro de version nest pas déjà présent en allant dans l'onglet *Packages & Registries*
```bash
curl -X PUT --header "PRIVATE-TOKEN: <API-TOKEN-WRITE-ACCESS>" \
     --upload-file /tmp/lolapy_conda.tar.gz \
     "https://gitlab.inria.fr/api/v4/projects/26214/packages/generic/lolapy_conda_pkg/<VERSION_NUMBER>/lolapy_conda.tar.gz"$ 
```

### Démarrer le faux lolapy

1. Générer l'image de fake_lolapy

``` bash
$ pwd
/lolapy
$ docker build -t lolapy_fake:1.4.2 -f docs/Dockerfile.fake_app .
```

2. Lancer fake_lolapy

``` bash
$ docker run lolapy_fake:1.4.2
```

Si besoin, monter un partage réseau et/ou utiliser un autre fichier de configuration:

``` bash
$ docker run --rm -p 8080:5000 -v $(pwd)/.env.experimental:/tmp/.env -e ENV_FILE=/tmp/.env lolapy_fake:1.4.2
```

### Constuire la doc

``` bash
$ mkdocs build
$ mkdocs serve
```
