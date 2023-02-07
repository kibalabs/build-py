FROM python:3.11.0-slim

RUN apt-get update && apt-get install --yes --no-install-recommends make

WORKDIR /app
COPY makefile $WORKDIR

COPY requirements.txt $WORKDIR
RUN make install

COPY . $WORKDIR
RUN pip install -e .
