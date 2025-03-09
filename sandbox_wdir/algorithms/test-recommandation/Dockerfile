FROM continuumio/miniconda3

ENV SOURCES=/sources
ENV PATH="/${SOURCES}:${PATH}"
ENV SURPRISE_DATA_FOLDER /tmp

RUN apt update && \
    apt install procps build-essential -y

COPY . ${SOURCES}
WORKDIR ${SOURCES}
RUN pip install -r requirements.txt
