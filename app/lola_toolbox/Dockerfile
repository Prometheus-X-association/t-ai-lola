FROM python:3.12.13-alpine
LABEL maintainer="Philippe Noel <philippe.noel@inria.fr>"
LABEL description="Image used to build linux version of lola_toolbox"

RUN apk update && \
    apk upgrade && \
    apk add \
    wget \
    build-base \
    binutils \
    git

COPY . /src

RUN pip install -r /src/requirements.txt && \
    pip install pyinstaller

ENTRYPOINT ["pyinstaller", "/src/main.spec", "--distpath", "/tmp/dist", "--workpath", "/tmp/build"]
