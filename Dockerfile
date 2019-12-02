FROM python:3.8-alpine

ENV PYTHONPATH /external_grader/

# Install required programs
RUN \
    apk update && \
    apk add --no-cache make openrc docker && \
    rc-update add docker boot

# Install Python requirements
COPY ./requirements /external_grader/requirements
WORKDIR /external_grader

RUN make requirements

# Copy grader files
COPY . /external_grader
