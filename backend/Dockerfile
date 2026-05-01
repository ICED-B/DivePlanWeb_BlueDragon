ARG VARIANT=3
FROM mcr.microsoft.com/devcontainers/python:3.13-bullseye

ENV FLASK_APP=run:app
ENV FLASK_DEBUG=1

COPY requirements.txt /tmp/pip-tmp/
RUN apt-get update && pip3 install -r /tmp/pip-tmp/requirements.txt

