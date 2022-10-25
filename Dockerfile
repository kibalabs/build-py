FROM python:3.11.0-slim

WORKDIR app

COPY requirements.txt $WORKDIR
RUN pip install -r requirements.txt

COPY . $WORKDIR
RUN pip install -e .
