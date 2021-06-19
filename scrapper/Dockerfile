# syntax=docker/dockerfile:1

FROM python:3-slim-buster

WORKDIR /app
COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT flask run --host=0.0.0.0
