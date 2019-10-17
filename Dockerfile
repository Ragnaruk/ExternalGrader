FROM python:3.8-alpine

RUN apk add --no-cache make vim
RUN apk add --no-cache ffmpeg

ENV PYTHONPATH /external_grader/

COPY . /external_grader
WORKDIR /external_grader

RUN make requirements
