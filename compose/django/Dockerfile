FROM python:3.8.3-buster

ENV PYTHONUNBUFFERED 1

ENV TERM=xterm

RUN apt-get update && pip3 install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
