FROM continuumio/miniconda3

ENV SOURCES=/sources

RUN apt update && \
    apt install procps build-essential -y

COPY ./data-import ${SOURCES}/data-import
COPY ./.env ${SOURCES}
WORKDIR ${SOURCES}
RUN pip install -r data-import/requirements.txt
#ENTRYPOINT ["python", "data-import/main.py"]
