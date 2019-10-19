FROM python:3.8-alpine

RUN \
    apk update && \
    apk add --no-cache openrc make vim docker && \
    rc-update add docker boot

ARG REQUIRED_PROGRAMS

RUN apk add --no-cache ${REQUIRED_PROGRAMS}

ENV PYTHONPATH /external_grader/

COPY . /external_grader
WORKDIR /external_grader

RUN make requirements
