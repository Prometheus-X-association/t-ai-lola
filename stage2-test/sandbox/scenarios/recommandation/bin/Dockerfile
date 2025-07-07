FROM continuumio/miniconda3:4.11.0
MAINTAINER Chahrazed LABBA <chahrazed.labba@loria.fr>

ENV SOURCES=/recommandation
ENV PATH="/${SOURCES}:${PATH}"
ENV SURPRISE_DATA_FOLDER /tmp

RUN apt update && \
    apt install procps build-essential -y

COPY . ${SOURCES}
WORKDIR ${SOURCES}

RUN pip install -r requirements.txt && \
    pip uninstall surprise -y && \
    conda install -c conda-forge scikit-surprise -y
