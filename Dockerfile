FROM python:3

RUN \
    apt -y update && \
    apt -y upgrade && \
    ln -sf /dev/stdout /grader.log && \
    apt -y install ffmpeg

ARG VERSION=10

RUN \
    git clone git://github.com/Ragnaruk/ExternalGrader.git && \
    pip install --no-cache-dir -r /ExternalGrader/requirements.txt

ENV PYTHONPATH /ExternalGrader/

COPY ./external_grader/config.py /ExternalGrader/external_grader/config.py

CMD [ "python", "./ExternalGrader/external_grader/" ]